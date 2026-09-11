#!/usr/bin/env python3
"""
Google Ads API WRITER (REST, no library) for {{COMPANY}}.
Same OAuth + MCC auth as channels/paid/google-ads/google_ads.py (puller). API v21.

SÛRETÉ : dry-run par défaut. Aucune mutation réelle tant que --execute
n'est PAS passé. Chaque commande imprime le payload exact avant tout envoi.

Commandes
---------
  # 1. Créer un objectif de conversion personnalisé (groupe d'actions)
  python3 channels/paid/google-ads/google_ads_write.py custom-goal-create \
      --name "Leads qualifiés IA" \
      --actions customers/<CUSTOMER_ID>/conversionActions/<ACTION_ID>

  # 2. Assigner cet objectif à une campagne (passe en goalConfigLevel=CAMPAIGN)
  python3 channels/paid/google-ads/google_ads_write.py campaign-goal-assign \
      --campaign <CAMPAIGN_ID> \
      --custom-goal customers/<CUSTOMER_ID>/customConversionGoals/<id>

  # 3. Revenir aux objectifs par défaut du compte (réversibilité)
  python3 channels/paid/google-ads/google_ads_write.py campaign-goal-reset --campaign <CAMPAIGN_ID>

  # Bonus : modifier un budget (id = campaignBudget id)
  python3 channels/paid/google-ads/google_ads_write.py budget-update --id <budget_id> --amount 65

Ajouter --execute pour exécuter réellement. Sinon : dry-run (affiche le payload).
"""
import sys, json, os
sys.path.insert(0, os.path.dirname(__file__))
from google_ads import get_access_token, API_VERSION, CID, MCC, DEV  # reuse puller auth
import requests


def parse_args(argv):
    out = {"_": []}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a.startswith("--"):
            key = a[2:]
            if i + 1 < len(argv) and not argv[i + 1].startswith("--"):
                out[key] = argv[i + 1]
                i += 2
            else:
                out[key] = True
                i += 1
        else:
            out["_"].append(a)
            i += 1
    return out


def mutate(service, operations, execute):
    """POST customers/{cid}/{service}:mutate — dry-run unless execute."""
    url = f"https://googleads.googleapis.com/{API_VERSION}/customers/{CID}/{service}:mutate"
    payload = {"operations": operations}
    print(f"\n--- {'EXECUTE' if execute else 'DRY-RUN'} : {service}:mutate ---")
    print(f"POST {url}")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    if not execute:
        print("\n[dry-run] rien envoyé. Ajouter --execute pour appliquer.")
        return None
    headers = {
        "Authorization": f"Bearer {get_access_token()}",
        "developer-token": DEV,
        "login-customer-id": MCC,
        "Content-Type": "application/json",
    }
    r = requests.post(url, headers=headers, json=payload)
    print(f"\nHTTP {r.status_code}")
    try:
        print(json.dumps(r.json(), indent=2, ensure_ascii=False))
    except Exception:
        print(r.text)
    r.raise_for_status()
    return r.json()


def cmd_custom_goal_create(args, execute):
    name = args.get("name")
    actions = args.get("actions")
    if not name or not actions:
        sys.exit("--name et --actions requis (--actions resourceName1,resourceName2)")
    action_rns = [a.strip() for a in str(actions).split(",") if a.strip()]
    ops = [{"create": {"name": name, "conversionActions": action_rns}}]
    mutate("customConversionGoals", ops, execute)


def cmd_campaign_goal_assign(args, execute):
    camp = args.get("campaign")
    goal = args.get("custom-goal")
    if not camp or not goal:
        sys.exit("--campaign <id> et --custom-goal <resourceName> requis")
    rn = f"customers/{CID}/conversionGoalCampaignConfigs/{camp}"
    ops = [{
        "update": {
            "resourceName": rn,
            "goalConfigLevel": "CAMPAIGN",
            "customConversionGoal": goal,
        },
        "updateMask": "goalConfigLevel,customConversionGoal",
    }]
    mutate("conversionGoalCampaignConfigs", ops, execute)


def cmd_campaign_goal_reset(args, execute):
    camp = args.get("campaign")
    if not camp:
        sys.exit("--campaign <id> requis")
    rn = f"customers/{CID}/conversionGoalCampaignConfigs/{camp}"
    ops = [{
        "update": {"resourceName": rn, "goalConfigLevel": "CUSTOMER"},
        "updateMask": "goalConfigLevel",
    }]
    mutate("conversionGoalCampaignConfigs", ops, execute)


def mutate_atomic(operations, execute, label=""):
    """POST customers/{cid}/googleAds:mutate (opérations mixtes, atomique)."""
    url = f"https://googleads.googleapis.com/{API_VERSION}/customers/{CID}/googleAds:mutate"
    payload = {"mutateOperations": operations}
    print(f"\n--- {'EXECUTE' if execute else 'DRY-RUN'} : googleAds:mutate [{label}] ---")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    if not execute:
        print(f"[dry-run] {label}: rien envoyé.")
        return None
    headers = {
        "Authorization": f"Bearer {get_access_token()}",
        "developer-token": DEV,
        "login-customer-id": MCC,
        "Content-Type": "application/json",
    }
    r = requests.post(url, headers=headers, json=payload)
    print(f"HTTP {r.status_code}")
    try:
        print(json.dumps(r.json(), indent=2, ensure_ascii=False))
    except Exception:
        print(r.text)
    r.raise_for_status()
    return r.json()


def _validate_plan(plan):
    """Garde-fou longueurs Google : titres <=30, descriptions <=90, RSA 3-15 / 2-4."""
    errs = []
    for g in plan["ad_groups"]:
        name = g["name"]
        h, d = g.get("headlines", []), g.get("descriptions", [])
        if not (3 <= len(h) <= 15):
            errs.append(f"[{name}] {len(h)} titres (attendu 3-15)")
        if not (2 <= len(d) <= 4):
            errs.append(f"[{name}] {len(d)} descriptions (attendu 2-4)")
        for t in h:
            txt = t["text"] if isinstance(t, dict) else t
            if len(txt) > 30:
                errs.append(f"[{name}] titre {len(txt)}c >30 : « {txt} »")
        for t in d:
            if len(t) > 90:
                errs.append(f"[{name}] description {len(t)}c >90 : « {t} »")
    return errs


def cmd_build_adgroups(args, execute):
    plan_path = args.get("plan")
    if not plan_path:
        sys.exit("--plan <fichier.json> requis")
    with open(plan_path, encoding="utf-8") as f:
        plan = json.load(f)

    errs = _validate_plan(plan)
    if errs:
        print("VALIDATION ÉCHOUÉE — corriger le plan avant tout push :")
        for e in errs:
            print("  ✗", e)
        sys.exit(1)
    print(f"✓ Validation OK : {len(plan['ad_groups'])} ad groups, longueurs conformes.")

    camp_rn = f"customers/{CID}/campaigns/{plan['campaign_id']}"
    # URL par défaut du plan ; chaque ad group peut la surcharger (LP dédiée par métier)
    url_default = plan.get("final_url")
    for g in plan["ad_groups"]:
        url = g.get("final_url") or url_default
        if not url:
            sys.exit(f"final_url manquant pour l'ad group « {g['name']} » et aucun défaut dans le plan")
        temp = f"customers/{CID}/adGroups/-1"
        ops = [{
            "adGroupOperation": {
                "create": {
                    "resourceName": temp,
                    "name": g["name"],
                    "campaign": camp_rn,
                    "status": "ENABLED",
                    "type": "SEARCH_STANDARD",
                }
            }
        }]
        for text, mt in g["keywords"]:
            ops.append({
                "adGroupCriterionOperation": {
                    "create": {
                        "adGroup": temp,
                        "status": "ENABLED",
                        "keyword": {"text": text, "matchType": mt},
                    }
                }
            })
        ops.append({
            "adGroupAdOperation": {
                "create": {
                    "adGroup": temp,
                    "status": "ENABLED",
                    "ad": {
                        "finalUrls": [url],
                        "responsiveSearchAd": {
                            "headlines": [
                                ({"text": h["text"], "pinnedField": h["pin"]}
                                 if isinstance(h, dict) and h.get("pin")
                                 else {"text": (h["text"] if isinstance(h, dict) else h)})
                                for h in g["headlines"]
                            ],
                            "descriptions": [{"text": t} for t in g["descriptions"]],
                        },
                    },
                }
            }
        })
        mutate_atomic(ops, execute, label=g["name"])


def _validate_rsa(headlines, descriptions):
    """Garde-fou RSA : 3-15 titres <=30c, 2-4 descriptions <=90c."""
    errs = []
    if not (3 <= len(headlines) <= 15):
        errs.append(f"{len(headlines)} titres (attendu 3-15)")
    if not (2 <= len(descriptions) <= 4):
        errs.append(f"{len(descriptions)} descriptions (attendu 2-4)")
    for h in headlines:
        if len(h["text"]) > 30:
            errs.append(f"titre {len(h['text'])}c >30 : « {h['text']} »")
    for d in descriptions:
        if len(d) > 90:
            errs.append(f"description {len(d)}c >90 : « {d} »")
    return errs


def cmd_campaign_create(args, execute):
    """Crée une campagne Search COMPLÈTE (budget + campagne + géo/langue + ad group + mots-clés + RSA)
    en UNE opération atomique. Lit un plan JSON. Voir channels/paid/google-ads/plans/marketing-digital-plan.json pour le format."""
    plan_path = args.get("plan")
    if not plan_path:
        sys.exit("--plan <fichier.json> requis")
    with open(plan_path, encoding="utf-8") as f:
        plan = json.load(f)

    headlines, descriptions = plan["headlines"], plan["descriptions"]
    errs = _validate_rsa(headlines, descriptions)
    if errs:
        print("VALIDATION ÉCHOUÉE — corriger le plan avant tout push :")
        for e in errs:
            print("  ✗", e)
        sys.exit(1)
    print(f"✓ Validation OK : {len(headlines)} titres, {len(descriptions)} descriptions, longueurs conformes.")

    tb = f"customers/{CID}/campaignBudgets/-1"   # resource names temporaires (atomique)
    tc = f"customers/{CID}/campaigns/-2"
    tag = f"customers/{CID}/adGroups/-3"
    geo = plan.get("geo", [2250])          # 2250 = France
    langs = plan.get("languages", [1002])  # 1002 = Français
    budget_micros = str(round(float(plan["budget_eur"]) * 1_000_000))

    ops = []
    ops.append({"campaignBudgetOperation": {"create": {
        "resourceName": tb, "name": plan["campaign_name"] + " — budget",
        "amountMicros": budget_micros, "deliveryMethod": "STANDARD", "explicitlyShared": False,
    }}})
    ops.append({"campaignOperation": {"create": {
        "resourceName": tc, "name": plan["campaign_name"], "status": plan.get("status", "ENABLED"),
        "advertisingChannelType": "SEARCH", "campaignBudget": tb,
        "containsEuPoliticalAdvertising": "DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING",  # requis API v21
        "maximizeConversions": {},   # Max Conversions SANS tCPA (campagne neuve, learning)
        "networkSettings": {"targetGoogleSearch": True, "targetSearchNetwork": False,
                            "targetContentNetwork": False, "targetPartnerSearchNetwork": False},
        "geoTargetTypeSetting": {"positiveGeoTargetType": "PRESENCE", "negativeGeoTargetType": "PRESENCE"},
    }}})
    for g in geo:
        ops.append({"campaignCriterionOperation": {"create": {
            "campaign": tc, "location": {"geoTargetConstant": f"geoTargetConstants/{g}"}}}})
    for l in langs:
        ops.append({"campaignCriterionOperation": {"create": {
            "campaign": tc, "language": {"languageConstant": f"languageConstants/{l}"}}}})
    ops.append({"adGroupOperation": {"create": {
        "resourceName": tag, "name": plan["ad_group_name"], "campaign": tc,
        "status": "ENABLED", "type": "SEARCH_STANDARD"}}})
    for text, mt in plan["keywords"]:
        ops.append({"adGroupCriterionOperation": {"create": {
            "adGroup": tag, "status": "ENABLED", "keyword": {"text": text, "matchType": mt}}}})
    rsa = {
        "headlines": [({"text": h["text"], "pinnedField": h["pin"]} if h.get("pin") else {"text": h["text"]}) for h in headlines],
        "descriptions": [{"text": d} for d in descriptions],
    }
    if plan.get("path1"):
        rsa["path1"] = plan["path1"]
    if plan.get("path2"):
        rsa["path2"] = plan["path2"]
    ops.append({"adGroupAdOperation": {"create": {
        "adGroup": tag, "status": "ENABLED",
        "ad": {"finalUrls": [plan["final_url"]], "responsiveSearchAd": rsa}}}})

    mutate_atomic(ops, execute, label=plan["campaign_name"])


def cmd_add_negatives(args, execute):
    """Ajoute des mots-clés négatifs (BROAD) au niveau campagne."""
    camp = args.get("campaign")
    kws = args.get("keywords")
    if not camp or not kws:
        sys.exit("--campaign <id> et --keywords \"mot1,mot2\" requis")
    ops = []
    for kw in [k.strip() for k in str(kws).split(",") if k.strip()]:
        ops.append({
            "create": {
                "campaign": f"customers/{CID}/campaigns/{camp}",
                "negative": True,
                "keyword": {"text": kw, "matchType": "BROAD"},
            }
        })
    mutate("campaignCriteria", ops, execute)


def cmd_set_tcpa(args, execute):
    """Ajoute un target CPA à une campagne Maximize Conversions (ou le retire si --amount 0)."""
    camp = args.get("campaign")
    amount = args.get("amount")
    if not camp or amount is None:
        sys.exit("--campaign <id> et --amount <euros> requis (0 pour retirer)")
    micros = str(round(float(amount) * 1_000_000))
    ops = [{
        "update": {
            "resourceName": f"customers/{CID}/campaigns/{camp}",
            "maximizeConversions": {"targetCpaMicros": micros},
        },
        "updateMask": "maximizeConversions.targetCpaMicros",
    }]
    mutate("campaigns", ops, execute)


def cmd_set_keyword_status(args, execute):
    """Change le statut de mots-clés d'un ad group : --adgroup <id> --keywords "a,b" --status PAUSED|ENABLED|REMOVED.
    Résout les criterion_id par le texte du mot-clé (tous match types confondus)."""
    ag = args.get("adgroup"); kws = args.get("keywords"); st = (args.get("status") or "PAUSED").upper()
    if not ag or not kws:
        sys.exit('--adgroup <id> et --keywords "a,b" requis')
    wanted = {k.strip().lower() for k in kws.split(",") if k.strip()}
    only_match = (args.get("match") or "").upper() or None
    import json as _j, urllib.request as _u
    tok = get_access_token()
    q = ("SELECT ad_group_criterion.criterion_id, ad_group_criterion.keyword.text, "
         "ad_group_criterion.keyword.match_type FROM ad_group_criterion "
         f"WHERE ad_group.id = {ag} AND ad_group_criterion.type = 'KEYWORD'")
    req = _u.Request(f"https://googleads.googleapis.com/{API_VERSION}/customers/{CID}/googleAds:search",
                     data=_j.dumps({"query": q}).encode(),
                     headers={"Authorization": f"Bearer {tok}", "developer-token": DEV,
                              "login-customer-id": MCC, "Content-Type": "application/json"})
    rows = _j.loads(_u.urlopen(req).read()).get("results", [])
    ops = []
    for r in rows:
        c = r["adGroupCriterion"]
        mt = c["keyword"]["matchType"]
        if only_match and mt != only_match:
            continue
        if c["keyword"]["text"].lower() in wanted:
            rn = f"customers/{CID}/adGroupCriteria/{ag}~{c['criterionId']}"
            if st == "REMOVED":
                # l'API refuse status=REMOVED en update : il faut une opération remove
                ops.append({"remove": rn})
            else:
                ops.append({"update": {"resourceName": rn, "status": st}, "updateMask": "status"})
            print(f"  {st:8} {c['keyword']['matchType']:7} {c['keyword']['text']}")
    if not ops:
        sys.exit("aucun mot-clé correspondant trouvé")
    mutate("adGroupCriteria", ops, execute)


def cmd_set_manual_cpc(args, execute):
    """Bascule une campagne en CPC manuel (Manual CPC). Réactive les CPC max des ad groups,
    inertes sous Maximize Conversions. --ecpc pour laisser l'eCPC actif (déconseillé : c'est
    l'auto-apply des recommandations Google qui l'avait rallumé le 2026-09-06)."""
    camp = args.get("campaign")
    if not camp:
        sys.exit("--campaign <id> requis")
    ops = [{
        "update": {
            "resourceName": f"customers/{CID}/campaigns/{camp}",
            "manualCpc": {"enhancedCpcEnabled": bool(args.get("ecpc"))},
        },
        "updateMask": "manual_cpc.enhanced_cpc_enabled",
    }]
    mutate("campaigns", ops, execute)


def cmd_set_adgroup_cpc(args, execute):
    """Fixe le CPC max (cpc_bid_micros) d'un ad group. Campagne en Manual CPC uniquement."""
    agid = args.get("adgroup") or args.get("id")
    amount = args.get("amount")
    if not agid or amount is None:
        sys.exit("--adgroup <id> et --amount <euros> requis")
    micros = str(round(float(amount) * 1_000_000))
    ops = [{
        "update": {
            "resourceName": f"customers/{CID}/adGroups/{agid}",
            "cpcBidMicros": micros,
        },
        "updateMask": "cpc_bid_micros",
    }]
    mutate("adGroups", ops, execute)


def cmd_geo_presence(args, execute):
    """Force le ciblage géo en PRESENCE (personnes physiquement dans la zone), anti-fuite hors-zone."""
    camp = args.get("campaign")
    if not camp:
        sys.exit("--campaign <id> requis")
    ops = [{
        "update": {
            "resourceName": f"customers/{CID}/campaigns/{camp}",
            "geoTargetTypeSetting": {"positiveGeoTargetType": "PRESENCE"},
        },
        "updateMask": "geoTargetTypeSetting.positiveGeoTargetType",
    }]
    mutate("campaigns", ops, execute)


def cmd_pause_adgroup(args, execute):
    agid = args.get("id")
    if not agid:
        sys.exit("--id <ad_group_id> requis")
    st = (args.get("status") or "PAUSED").upper()
    ops = [{
        "update": {
            "resourceName": f"customers/{CID}/adGroups/{agid}",
            "status": st,
        },
        "updateMask": "status",
    }]
    mutate("adGroups", ops, execute)


def cmd_remove_adgroup(args, execute):
    agid = args.get("id")
    if not agid:
        sys.exit("--id <ad_group_id> requis")
    ops = [{"remove": f"customers/{CID}/adGroups/{agid}"}]
    mutate("adGroups", ops, execute)


def cmd_budget_update(args, execute):
    bid = args.get("id")
    amount = args.get("amount")
    if not bid or not amount:
        sys.exit("--id <budget_id> et --amount <euros> requis")
    micros = str(round(float(amount) * 1_000_000))
    rn = f"customers/{CID}/campaignBudgets/{bid}"
    ops = [{
        "update": {"resourceName": rn, "amountMicros": micros},
        "updateMask": "amountMicros",
    }]
    mutate("campaignBudgets", ops, execute)


def cmd_add_keywords(args, execute):
    """Ajoute des mots-clés POSITIFS à un ad group existant. Match phrase par défaut."""
    agid = args.get("adgroup")
    kws = args.get("keywords")
    match = str(args.get("match") or "PHRASE").upper()
    if not agid or not kws:
        sys.exit('--adgroup <ad_group_id> et --keywords "mot1,mot2" requis (option --match PHRASE|EXACT|BROAD)')
    ag = f"customers/{CID}/adGroups/{agid}"
    ops = []
    for kw in [k.strip() for k in str(kws).split(",") if k.strip()]:
        ops.append({"create": {
            "adGroup": ag,
            "status": "ENABLED",
            "keyword": {"text": kw, "matchType": match},
        }})
    mutate("adGroupCriteria", ops, execute)


def cmd_sitelinks_create(args, execute):
    """Crée des sitelinks (assets) et les rattache à une campagne. Atomique.
    Plan JSON : {"campaign_id":"...", "sitelinks":[{"text","url","desc1"?,"desc2"?}]}
    Garde-fous Google : text <=25, desc1/desc2 <=35."""
    plan_path = args.get("plan")
    if not plan_path:
        sys.exit('--plan <json> requis : {"campaign_id":"...","sitelinks":[{"text","url","desc1","desc2"}]}')
    with open(plan_path, encoding="utf-8") as f:
        plan = json.load(f)
    camp = plan["campaign_id"]
    sitelinks = plan["sitelinks"]
    # validation longueurs
    errs = []
    for sl in sitelinks:
        if not sl.get("text") or not sl.get("url"):
            errs.append(f"sitelink sans text/url : {sl}")
        if len(sl.get("text", "")) > 25:
            errs.append(f'text {len(sl["text"])}c >25 : « {sl["text"]} »')
        for k in ("desc1", "desc2"):
            if sl.get(k) and len(sl[k]) > 35:
                errs.append(f'{k} {len(sl[k])}c >35 : « {sl[k]} »')
    if errs:
        print("Longueurs invalides :")
        for e in errs:
            print("  - " + e)
        sys.exit(1)
    camp_rn = f"customers/{CID}/campaigns/{camp}"
    ops = []
    for i, sl in enumerate(sitelinks):
        asset_rn = f"customers/{CID}/assets/{-(i+1)}"
        sitelink = {"linkText": sl["text"]}
        if sl.get("desc1"):
            sitelink["description1"] = sl["desc1"]
        if sl.get("desc2"):
            sitelink["description2"] = sl["desc2"]
        ops.append({"assetOperation": {"create": {
            "resourceName": asset_rn,
            "finalUrls": [sl["url"]],
            "sitelinkAsset": sitelink,
        }}})
        ops.append({"campaignAssetOperation": {"create": {
            "campaign": camp_rn,
            "asset": asset_rn,
            "fieldType": "SITELINK",
        }}})
    mutate_atomic(ops, execute, label=f"sitelinks x{len(sitelinks)} → campagne {camp}")


def cmd_set_campaign_status(args, execute):
    """Passe une campagne ENABLED / PAUSED / REMOVED."""
    camp = args.get("campaign")
    status = str(args.get("status") or "").upper()
    if not camp or status not in ("ENABLED", "PAUSED", "REMOVED"):
        sys.exit("--campaign <id> et --status ENABLED|PAUSED|REMOVED requis")
    ops = [{"update": {"resourceName": f"customers/{CID}/campaigns/{camp}", "status": status},
            "updateMask": "status"}]
    mutate("campaigns", ops, execute)


COMMANDS = {
    "custom-goal-create": cmd_custom_goal_create,
    "campaign-goal-assign": cmd_campaign_goal_assign,
    "campaign-goal-reset": cmd_campaign_goal_reset,
    "build-adgroups": cmd_build_adgroups,
    "campaign-create": cmd_campaign_create,
    "pause-adgroup": cmd_pause_adgroup,
    "remove-adgroup": cmd_remove_adgroup,
    "geo-presence": cmd_geo_presence,
    "set-tcpa": cmd_set_tcpa,
    "set-adgroup-cpc": cmd_set_adgroup_cpc,
    "set-manual-cpc": cmd_set_manual_cpc,
    "set-keyword-status": cmd_set_keyword_status,
    "add-negatives": cmd_add_negatives,
    "budget-update": cmd_budget_update,
    "add-keywords": cmd_add_keywords,
    "sitelinks-create": cmd_sitelinks_create,
    "set-campaign-status": cmd_set_campaign_status,
}


def main():
    args = parse_args(sys.argv[1:])
    cmd = args["_"][0] if args["_"] else None
    execute = bool(args.get("execute"))
    if cmd not in COMMANDS:
        print("Commandes : " + ", ".join(COMMANDS))
        print("Ajouter --execute pour appliquer (sinon dry-run).")
        sys.exit(0 if cmd is None else 1)
    COMMANDS[cmd](args, execute)


if __name__ == "__main__":
    main()
