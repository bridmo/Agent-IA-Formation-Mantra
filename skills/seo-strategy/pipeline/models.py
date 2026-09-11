"""
Data models for the SEO strategy pipeline.
Defines the structure of each phase's output so nothing gets forgotten.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Persona(Enum):
    P1_SENIOR_TRANSITION = "P1"
    P2_RESPONSABLE_STAGNE = "P2"
    P3_FREELANCE = "P3"
    P4_CMO = "P4"
    P5_FONDATEUR = "P5"


class ContentType(Enum):
    COMPARATIF = "Comparatif outils"
    GUIDE_OUTIL = "Guide outil"
    GUIDE_FEATURE = "Feature guide"
    GUIDE_METHODE = "Méthode guide"
    GUIDE_PRATIQUE = "Guide pratique"
    LISTICLE = "Listicle"
    PILLAR = "Pillar"
    DEFINITION = "Définition"
    FICHE_METIER = "Fiche métier"
    COMPARATIF_FORMATION = "Comparatif formations"


class KeywordCategory(Enum):
    LP = "LP (landing page)"
    TOOL = "Tool keyword"
    TOOL_FEATURE = "Tool feature"
    TOOL_USAGE = "Tool usage"
    TOOL_COMPARISON = "Tool comparison"
    NEWSJACKING = "Newsjacking"
    REGULATION = "Regulation"
    CONCEPT = "Concept"
    METHOD = "Method"
    PROBLEM = "Problem"
    CAREER = "Career"


class ArticleStatus(Enum):
    NEW = "NEW"
    REFRESH = "REFRESH"


class ContentStatus(Enum):
    PROTECT = "PROTECT"
    REFRESH = "REFRESH"
    ABANDON = "ABANDON"
    MISSING = "MISSING"


class Priority(Enum):
    URGENT = "🔴"
    IMPORTANT = "🟡"
    PLANNED = "🟢"


# --- Title formulas that rank (proven in FR market 2025-2026) ---

TITLE_FORMULAS = {
    ContentType.COMPARATIF: [
        "{A} vs {B} : quel(le) {categorie} choisir en {annee} ?",
        "{A} vs {B} : comparatif complet pour {cible}",
        "{Outil} : gratuit ou payant ? Ce que {cible} ratent sans la version Pro",
    ],
    ContentType.GUIDE_OUTIL: [
        "{Outil} : guide complet pour {usage_cible}",
        "{Outil} : le guide {annee} pour {cible}",
    ],
    ContentType.GUIDE_FEATURE: [
        "{Feature} : guide pour {action_concrete}",
    ],
    ContentType.GUIDE_METHODE: [
        "{Methode} : méthode complète pour {resultat_concret}",
        "{Methode} : guide complet pour {cible} en {annee}",
    ],
    ContentType.GUIDE_PRATIQUE: [
        "{Sujet} : par où commencer en {annee}",
        "{Sujet} en {contexte} : guide pour {action}",
    ],
    ContentType.LISTICLE: [
        "Les meilleurs {choses} pour {cible} : guide par {angle}",
        "Les {N} meilleur(e)s {choses} en {annee}",
    ],
    ContentType.PILLAR: [
        "{Keyword} : le guide ultime pour {action_concrete}",
    ],
    ContentType.DEFINITION: [
        "{Concept} : qu'est-ce que c'est et {pourquoi_ca_compte}",
        "{Concept} : définition, {element_1} et {element_2} en {annee}",
    ],
    ContentType.FICHE_METIER: [
        "{Metier} : salaire, compétences et évolution {annee}",
    ],
    ContentType.COMPARATIF_FORMATION: [
        "Les {N} meilleures formations {discipline} en {annee}",
    ],
}


@dataclass
class Product:
    name: str
    url: str
    price: int
    duration: str
    themes: list[str]  # extracted from program
    tools: list[str]   # tools taught
    pct_deals: float   # % of total deals


@dataclass
class Keyword:
    keyword: str
    volume_fr: int
    kd: Optional[int]
    cpc: Optional[int]
    intent: str  # informational, commercial, transactional
    category: KeywordCategory
    product: str  # which formation it serves
    product_bridge: str  # "direct", "outil", "audience"
    personas: list[Persona]
    icp_pain_point: Optional[str]  # which pain point it addresses
    icp_trigger: Optional[str]  # which purchase trigger
    current_position: Optional[int]  # our current rank, if any
    current_url: Optional[str]


@dataclass
class SerpResult:
    keyword: str
    top_5: list[dict]  # [{url, domain_rating, traffic}]
    has_school_competitor: bool
    dominant_format: str  # what type of content ranks
    angle_gap: str  # what angle is missing from SERP


@dataclass
class ExistingContent:
    url: str
    keyword: str
    position: Optional[int]
    traffic: int
    status: ContentStatus
    action: str  # what to do
    product_served: Optional[str]


@dataclass
class Article:
    number: int
    title: str  # MUST be a complete title from TITLE_FORMULAS, never a raw keyword
    keyword: str
    keyword_secondary: list[str]
    volume_fr: int
    kd: Optional[int]
    content_type: ContentType
    status: ArticleStatus
    product: str  # formation served
    product_bridge: str
    personas: list[Persona]
    icp_justification: str  # why this article serves the ICP
    serp_angle: str  # what angle we take vs current SERP
    cluster: str  # which cluster (A, B, C...)
    week: str  # S1, S2, etc.
    effort_hours: float
    score: int
    score_breakdown: str  # "Product 2 x Demand 3 x Intent 2 x Effort 3 = 36 + 0 adj"
    priority: Priority
    internal_links_in: list[str]  # pages that should link TO this article
    internal_links_out: list[str]  # pages this article links TO
    cta_formation_url: str


@dataclass
class Backlog:
    articles: list[Article]
    refreshes: list[ExistingContent]
    lp_optimizations: list[dict]
    total_volume: int
    total_effort_hours: float

    @property
    def format_mix(self) -> dict[ContentType, int]:
        """Count articles by content type."""
        mix = {}
        for a in self.articles:
            mix[a.content_type] = mix.get(a.content_type, 0) + 1
        return mix

    @property
    def persona_coverage(self) -> dict[Persona, int]:
        """Count how many articles serve each persona."""
        coverage = {}
        for a in self.articles:
            for p in a.personas:
                coverage[p] = coverage.get(p, 0) + 1
        return coverage
