"""Economics layer — décomposition CA = Volume × Panier + bundle penetration.

Permet de détecter quand le panier moyen change structurellement (ex: réforme financement public
de fév-mars 2026 → plafond 1500€ → bundle ne se finance plus).

Métriques produites :
- CA = N deals × avg deal (décomposition explicite)
- Bundle penetration (% deals multi-formations basé sur dealname)
- Formation mix (combien de chaque formation vendue)
- Rupture structurelle : alerte si avg deal dévie >10% vs baseline 3 mois
"""
from __future__ import annotations
import re
import statistics
from collections import Counter
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional


# Source de vérité {{COMPANY}} : champs HubSpot deal
#   - `product` (enum multi-checkbox, séparateur `;`) = formations VENDUES (génèrent du CA)
#   - `product_offert` (enum multi-checkbox, séparateur `;`) = produits OFFERTS (bonus, pas vendus)
#
# Formations primaires VENDUES (génèrent du CA, comptent dans bundle) :
PRIMARY_PRODUCTS_SOLD = {"GM", "IA generative", "IA automation"}

# Produits TOUJOURS offerts (cadeau bundle), même si stockés dans le champ `product` HubSpot.
# Décision {{COMPANY}} : Promotion emploi est un add-on offert, jamais vendu en propre.
# On le tracke en `offert` quel que soit le champ source pour ne pas perdre la visibilité.
ALWAYS_OFFERED_PRODUCTS = {"Promotion emploi"}

# Mapping legacy : valeurs anciennes → valeurs actuelles
LEGACY_PRODUCT_MAP = {
    "GH & IA": "GM",  # rename HubSpot, ancienne valeur conservée sur deals pré-rename
}


def normalize_product(raw: str) -> str:
    """Normalize a single product value (handle legacy renames)."""
    raw = (raw or "").strip()
    return LEGACY_PRODUCT_MAP.get(raw, raw)


def parse_products(product_value: Optional[str], product_offert_value: Optional[str] = None) -> Dict[str, List[str]]:
    """Parse les champs `product` et `product_offert` (HubSpot multi-checkbox stocké comme str séparé par `;`).

    Décision {{COMPANY}} : Promotion emploi est TOUJOURS un produit offert (jamais vendu),
    même quand il apparaît dans le champ `product`. Il est donc déplacé automatiquement
    vers `offert` pour ne pas fausser le bundle count (qui compte uniquement les ventes réelles).

    Returns :
      - 'sold' : produits vraiment vendus (génèrent du CA) — GM, IA gen, IA auto
      - 'offert' : produits offerts en cadeau (incluant Promotion emploi qu'il vienne de product ou product_offert)
      - 'n_sold' / 'n_offert' / 'is_bundle' (≥2 sold)
    """
    sold = []
    offert = []

    # Parse `product` field : déplacer Promotion emploi vers `offert`, garder le reste en `sold`
    if product_value:
        for raw in product_value.split(";"):
            normalized = normalize_product(raw)
            if not normalized:
                continue
            if normalized in ALWAYS_OFFERED_PRODUCTS:
                # Force le tracking en offert même si dans `product` HubSpot
                if normalized not in offert:
                    offert.append(f"{normalized} (depuis product, forcé en offert)")
            elif normalized in PRIMARY_PRODUCTS_SOLD:
                sold.append(normalized)
            else:
                # Valeur inconnue, on l'ignore mais on pourrait logger
                pass

    # Parse `product_offert` field
    if product_offert_value:
        for raw in product_offert_value.split(";"):
            v = raw.strip()
            if v and v.lower() != "aucun":
                # Nettoyage : "Promotion emploi [content]" → "Promotion emploi"
                v_clean = v.replace(" [content]", "").strip()
                # Normalize legacy si besoin
                v_clean = normalize_product(v_clean)
                if v_clean not in [o.split(" (")[0] for o in offert]:
                    offert.append(v_clean)

    return {
        "sold": sold,
        "offert": offert,
        "n_sold": len(sold),
        "n_offert": len(offert),
        "is_bundle": len(sold) >= 2,  # bundle = ≥2 produits VENDUS (Promotion emploi exclue)
    }


def compute_economics(closed_won_deals: List[dict]) -> dict:
    """Decompose CA = Volume × Avg deal, with bundle + formation analysis."""
    if not closed_won_deals:
        return {
            "ca_total": 0, "deal_count": 0, "avg_deal": 0, "median_deal": 0,
            "bundle_count": 0, "bundle_pct": 0, "single_count": 0,
            "formation_counts": {},
            "deals_by_price_bucket": {},
        }

    # Bundle detection : on combine 2 signaux pour catcher les "stealth bundles"
    # (deals où le champ `product` ne contient qu'1 valeur mais l'amount révèle un bundle).
    # Seuil amount : > 1700€ = bundle. Single GM après la réforme du financement = 1600€.
    BUNDLE_AMOUNT_THRESHOLD = 1700

    amounts = []
    bundle_count = 0
    single_count = 0
    no_product_count = 0  # deal sans `product` rempli (rare)
    bundle_by_product_count = 0  # bundle détecté via product field (≥2 products)
    bundle_by_amount_count = 0   # bundle détecté uniquement via amount > 1700€ ("stealth")
    product_counts = Counter()
    offert_counts = Counter()
    deals_data = []
    for d in closed_won_deals:
        p = d["properties"]
        amt = float(p.get("amount") or 0)
        parsed = parse_products(p.get("product"), p.get("product_offert"))
        n_sold = parsed["n_sold"]
        bundle_by_product = parsed["is_bundle"]  # ≥2 products in `product` field
        bundle_by_amount = amt > BUNDLE_AMOUNT_THRESHOLD
        is_bundle = bundle_by_product or bundle_by_amount

        if n_sold == 0 and amt == 0:
            no_product_count += 1
        elif is_bundle:
            bundle_count += 1
            if bundle_by_product:
                bundle_by_product_count += 1
            elif bundle_by_amount:
                bundle_by_amount_count += 1
        else:
            single_count += 1

        for prod in parsed["sold"]:
            product_counts[prod] += 1
        for prod in parsed["offert"]:
            offert_counts[prod] += 1
        amounts.append(amt)
        deals_data.append({
            "amount": amt, "is_bundle": is_bundle, "n_sold": n_sold,
            "sold": parsed["sold"], "offert": parsed["offert"],
            "bundle_detected_via": ("product_field" if bundle_by_product else ("amount_threshold" if bundle_by_amount else None)),
        })

    total = sum(amounts)
    n = len(amounts)

    # Price distribution buckets
    buckets = Counter()
    for a in amounts:
        if a < 1700: buckets["<1700"] += 1
        elif a < 2200: buckets["1700-2199"] += 1
        elif a < 2800: buckets["2200-2799"] += 1
        elif a < 3500: buckets["2800-3499"] += 1
        else: buckets["3500+"] += 1

    # Avg deal: bundle vs single
    bundle_amts = [d["amount"] for d in deals_data if d["is_bundle"]]
    single_amts = [d["amount"] for d in deals_data if not d["is_bundle"]]

    # Counts single/bundle excluent les deals sans `product` rempli
    parseable = bundle_count + single_count
    return {
        "ca_total": total,
        "deal_count": n,
        "avg_deal": total / n,
        "median_deal": statistics.median(amounts),
        "min_deal": min(amounts),
        "max_deal": max(amounts),
        "bundle_count": bundle_count,
        "bundle_pct": (bundle_count / parseable * 100) if parseable else 0,
        "bundle_by_product_field": bundle_by_product_count,    # détecté via ≥2 products dans `product`
        "bundle_by_amount_only": bundle_by_amount_count,       # "stealth bundle" (1 product visible mais amount > 1700€)
        "bundle_amount_threshold_eur": BUNDLE_AMOUNT_THRESHOLD,
        "single_count": single_count,
        "no_product_filled_count": no_product_count,
        "avg_bundle_deal": statistics.mean(bundle_amts) if bundle_amts else 0,
        "avg_single_deal": statistics.mean(single_amts) if single_amts else 0,
        "product_counts_sold": dict(product_counts),
        "product_counts_offert": dict(offert_counts),
        "deals_by_price_bucket": dict(buckets),
    }


def detect_structural_break(
    current_avg_deal: float,
    baseline_3m_avg_deal: float,
    threshold_pct: float = 10,
) -> dict:
    """Detect if current avg deal deviates >threshold_pct vs 3-month baseline.

    Returns alert with context for human investigation.
    """
    if baseline_3m_avg_deal == 0:
        return {"alert": False, "reason": "no baseline data"}
    delta_pct = (current_avg_deal - baseline_3m_avg_deal) / baseline_3m_avg_deal * 100
    is_break = abs(delta_pct) > threshold_pct
    direction = "drop" if delta_pct < 0 else "increase"
    return {
        "alert": is_break,
        "current_avg_deal": current_avg_deal,
        "baseline_3m_avg_deal": baseline_3m_avg_deal,
        "delta_pct": delta_pct,
        "direction": direction,
        "threshold_pct": threshold_pct,
        "interpretation": (
            f"⚠️ Rupture structurelle détectée : panier moyen {direction} de {abs(delta_pct):.0f}% "
            f"vs baseline 3 mois (target {baseline_3m_avg_deal:,.0f}€ → observé {current_avg_deal:,.0f}€). "
            f"Hypothèses : changement de mix produit, pricing, régulation, ou rupture commerciale. "
            f"Vérifier avec contexte qualitatif."
            if is_break else
            f"OK : panier moyen aligné à baseline ({delta_pct:+.0f}% vs 3 mois)."
        ),
    }


def compute_target_decomposition(
    ca_observed: float,
    avg_deal_observed: float,
    deal_count_observed: float,
    target_ca: float,
) -> dict:
    """Decompose target into volume×panier scenarios.

    Given current observed values + target, show what's needed to close gap:
    - Pure volume play (keep panier, scale deals)
    - Pure panier play (keep volume, raise panier)
    - Combo
    """
    gap = target_ca - ca_observed
    deals_needed_at_current_panier = (target_ca / avg_deal_observed) if avg_deal_observed > 0 else 0
    panier_needed_at_current_volume = (target_ca / deal_count_observed) if deal_count_observed > 0 else 0
    return {
        "target_ca": target_ca,
        "observed_ca": ca_observed,
        "gap": gap,
        "gap_pct": (gap / target_ca * 100) if target_ca > 0 else 0,
        "observed_deals": deal_count_observed,
        "observed_avg_deal": avg_deal_observed,
        "scenario_volume_only": {
            "deals_needed": deals_needed_at_current_panier,
            "deals_to_add": deals_needed_at_current_panier - deal_count_observed,
            "uplift_pct": ((deals_needed_at_current_panier - deal_count_observed) / deal_count_observed * 100)
                if deal_count_observed > 0 else 0,
        },
        "scenario_panier_only": {
            "panier_needed": panier_needed_at_current_volume,
            "panier_to_add": panier_needed_at_current_volume - avg_deal_observed,
            "uplift_pct": ((panier_needed_at_current_volume - avg_deal_observed) / avg_deal_observed * 100)
                if avg_deal_observed > 0 else 0,
        },
        "scenario_combo": {
            "deals": deal_count_observed * 1.1,
            "panier": avg_deal_observed * (target_ca / (ca_observed * 1.1)) if ca_observed > 0 else 0,
            "narrative": f"+10% deals × +{((target_ca / (ca_observed * 1.1)) - 1) * 100:.0f}% panier",
        } if ca_observed > 0 else None,
    }
