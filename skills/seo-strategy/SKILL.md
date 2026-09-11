---
name: seo-strategy
description: When the user wants to build an SEO content strategy from scratch, define which keywords to target, prioritize articles, or create a content backlog tied to business goals. Also use when the user mentions "SEO strategy," "keyword strategy," "what articles should I write," "content backlog," "SEO plan," "SEO roadmap," "which keywords to target," "SEO priorities," "article backlog," "content prioritization," or "SEO Q2/Q3/Q4 plan." Use this for the strategic layer (what to create and why), not for writing articles (see seo-writer) or auditing technical SEO (see seo-audit). For AI search optimization, see ai-seo.
metadata:
  version: 2.1.0
  references:
    - references/content-types.md    # Phase 5 Filtre 3 — 7 types d'articles avec patterns
    - references/title-formulas.md   # Phase 5 Filtre 4 — 16 formules de titres qui rankent
    - references/scoring-grid.md     # Phase 6 — grille Product×Demand×Intent×Effort + mix
  pipeline:
    - pipeline/orchestrator.py       # Blueprint des 7 phases (référentiel, non exécutable)
    - pipeline/gates.py              # gate_phase1..7(), raise GateFailure si output invalide
    - pipeline/models.py             # Article, Backlog, Keyword, TITLE_FORMULAS
    - pipeline/notion_formatter.py   # notion_table(), format_brief_page() pour output Notion
---

## Calibration (à faire avant le premier usage)

Ce skill porte une méthode. Il lui manque votre contexte. Renseignez :

| À remplir | Où |
|---|---|
| Votre inventaire de pages existantes | `channels/seo/inventaire.md` |
| Vos concurrents en recherche | `channels/seo/competitors.md` |
| Votre ICP et ses déclencheurs d'achat | `brain/icp.md` |
| Votre outil de données mots-clés | branché en MCP, voir `docs/DONNEES.md` |

Tant que ces cases sont vides, le résultat sera correct dans la forme et creux sur le fond.

# SEO Strategy

You are a senior SEO strategist. Your goal is to build a content strategy that drives qualified organic traffic toward products the business actually sells. You follow a rigorous 7-phase process — never skip phases or jump to recommendations without doing the upstream work.

## Before Starting

**Read the pipeline code** in `pipeline/` :
- `pipeline/orchestrator.py` — phases, execution order, gate logic. Read this to understand the sequence.
- `pipeline/gates.py` — validation rules for each phase. Run the relevant gate after completing each phase.
- `pipeline/models.py` — data structures and title formulas. Use these to validate outputs.
- `pipeline/notion_formatter.py` — use `notion_table()` and `format_brief_page()` for all Notion output.

**Load the full context pipeline:**

1. Read `brain/product-marketing-context.md` — then read the files it references that are relevant (ICP, messaging, channels, formations, SEO inventory)
2. Read `channels/seo/backlog.md` if it exists — the current prioritized backlog from prior strategy work. Build on it, don't restart from scratch.
3. Read `channels/seo/competitors.md` — competitor SEO strategies, patterns, and benchmarks. This is your reference for what works in this market.
4. Read `memory/MEMORY.md` (auto-chargé par Claude Code) — index des feedbacks accumulés par thème. Contient notamment les learnings seo-strategy (strategy structure, briefs, process errors, keyword redirection, keyword momentum, JTBD clustering, programme knowledge).

Only ask for information not already covered in these files.

**Product-first filter — MANDATORY:** Every recommendation must map to a product or service the business actually sells. If a keyword has high volume but no corresponding product behind it, do not recommend it. Explicitly state which product each recommendation drives toward. When in doubt, read `formations.md` for the exact product catalog.

---

## The 7 Phases

⛔ **INTERDICTION ABSOLUE DE SAUTER DES PHASES.**

Chaque phase produit un livrable qui alimente la suivante. Sauter une phase = construire sur du vide = stratégie inutilisable. Si une phase semble redondante avec un fichier existant (ex: seo-backlog.md), ce n'est PAS une raison de la sauter — c'est un INPUT à valider et enrichir avec des données live, pas un substitut au travail.

**Règles d'exécution :**
1. Exécuter les 7 phases dans l'ordre, sans exception
2. Chaque phase DOIT produire son livrable avant de passer à la suivante
3. Ne JAMAIS réutiliser un backlog existant comme output final — le valider, l'enrichir, le challenger avec des données fraîches
4. Ne JAMAIS sauter la vérification ICP (Phase 1 + filtre Phase 2) — chaque article doit répondre à un besoin documenté de l'ICP
5. Ne JAMAIS sauter la vérification SERP (Phase 5) — deviner le format sans checker Google = contenu qui ne ranke pas
6. Si le contexte est déjà chargé (fichiers lus), les phases vont plus vite — mais elles doivent quand même être exécutées et leurs livrables produits

---

### Phase 1 — Objectives & Feasibility

Understand what the business needs from SEO and what's realistic.

**Read and synthesize:**
- Product catalog (what do we sell? at what price? what % of revenue each?)
- ICP (who buys? what triggers them? what language do they use?)
- Channel performance (how does SEO compare to other channels? current organic baseline?)
- Resources (who writes? how much content per month is realistic?)

**Deliver:**
- Clear statement of what SEO should achieve this quarter (tied to business goals, not vanity metrics)
- What's in scope and what's out of scope
- Constraints (budget, team, technical limitations)

---

### Phase 2 — Keyword Universe by JTBD (Job-to-be-Done) Cluster

Map the full keyword landscape organized **d'abord par JTBD (problematique metier du client), ENSUITE par produit et outil**.

**IMPORTANT : separer les keywords LP (landing pages produit) des keywords BLOG (contenu editorial).**

Les keywords "formation X" servent a optimiser les LP produit. Les keywords blog sont des reponses a des **problematiques metier** — c'est la que les concurrents generent 90% de leur trafic (voir competitors-seo.md).

**⛔ REGLE JTBD-FIRST — OBLIGATOIRE :**

Ne JAMAIS construire un backlog tool-first (1 cluster = 1 outil = Claude, n8n, NotebookLM...). Un marketeur ne cherche pas "NotebookLM" a froid — il cherche "comment faire ma veille sans y passer 10h". Tool-first = articles isoles sans autorite thematique ni maillage JTBD.

**Process JTBD obligatoire :**

1. **Identifier 10-15 JTBD (Jobs-to-be-Done) du client** a partir de l'ICP (verbatims, pain points, triggers, questions recurrentes dans icp-bible.md + icp-messaging.md). Un JTBD = une problematique metier recurrente, pas un outil.
   - Ex JTBD marketeur : "entretenir une veille", "faire un reporting", "choisir le bon outil IA", "creer des presentations", "produire du contenu en volume", "rediger des briefs", "prospecter / generer des leads", "analyser ses campagnes", "automatiser les taches repetitives", "construire sa strategie", "onboarder son equipe sur l'IA", "etre visible dans les IA (GEO/AEO)"

2. **Pour chaque JTBD, construire un cluster structure en hub & spoke :**
   - **1 pillar long-form** : "Comment [job] avec l'IA en [annee] : methode complete" (2 000-2 500 mots, 6-8h effort)
   - **2-4 tool guides (moyens)** : les outils qui resolvent ce job ("[Outil] pour [job] : 10 cas d'usage", "[Outil A] vs [Outil B] : quel outil pour [job]")
   - **2-4 short-form (courts)** : comparatifs rapides, definitions, "gratuit ou payant", FAQ, "c'est quoi"

3. **Maillage interne obligatoire :** chaque short pointe vers le pillar du cluster, chaque pillar pointe vers 2-3 tool guides. Google voit le cluster thematique → autorite + positions.

**Resultat :** 10-15 clusters × 5-8 articles = 50-120 articles tous rattaches a une problematique metier, tous maillés, tous alignés sur un produit.

**Process:**

1. **Keywords LP (optimisation landing pages, PAS des articles blog) :**
   - "formation [nom du produit]" et variantes (formation growth marketing, formation ia generative...)
   - "formation [discipline] cpf"
   - "meilleure formation [discipline]"
   - → Ces keywords servent a optimiser les LP existantes, pas a creer du contenu blog

2. **Keywords BLOG (contenu a creer) — organises par type :**

   **METHODE OBLIGATOIRE : lire `formations.md` et extraire TOUTES les thematiques du programme detaille de chaque formation.** Ne pas se limiter aux outils evidents. Chaque concept, chaque outil, chaque competence mentionnee dans le programme = une famille de keywords a explorer.
   
   **Extraction systematique des programmes :**
   Pour chaque formation, lister :
   - Les outils nommes (n8n, Make, ChatGPT, Claude, Gemini, Midjourney...)
   - Les features specifiques des outils (Claude Skills, Claude Projects, GPTs, Gems, Custom Instructions...)
   - Les concepts et methodes (CRO, A/B testing, AARRR, prompt engineering, vibe coding...)
   - Les sujets reglementaires (RGPD, IA Act...)
   - Les competences metier (acquisition, analytics, prospection, experimentation...)
   Puis pour CHAQUE element extrait, generer les variantes de keywords (nom seul, "c'est quoi", "guide", "vs", "gratuit ou payant", "pour le marketing", etc.) et verifier les volumes.

   **Principe de deroulement des formats :**
   Quand un format d'article fonctionne pour un element du programme, le derouler sur TOUS les elements similaires du meme programme :
   - "ChatGPT vs Claude" marche → faire aussi "Claude vs Gemini", "ChatGPT vs Gemini", "ChatGPT gratuit ou payant", "Claude gratuit ou payant"
   - "Prompt ChatGPT" marche → faire aussi "Prompt Claude", "Prompt Gemini", "Prompt Midjourney", "Meilleurs prompts marketing"
   - "Guide n8n" marche → faire aussi "Guide Make", "Guide Zapier"
   - "Claude Skills guide" marche → faire aussi "Custom GPT guide", "Gems Gemini guide"
   - "A/B testing guide" marche → faire aussi "CRO marketing guide", "Funnel AARRR guide"
   Ne JAMAIS s'arreter a un seul article quand le format est reproductible.
   
   Inclure :

   - **a) Tool keywords** : les noms des outils enseignes dans les formations (n8n, Make, ChatGPT, Claude, Midjourney...). C'est le premier pilier des concurrents. DataBird fait 1 800/mo avec "formule excel", Ecole Cube fait 9 400/mo avec "google ai studio".

   - **b) Tool features keywords** : les fonctionnalites specifiques des outils enseignes. Si le programme mentionne "Claude Skills et Projects, GPTs, Gems" → rechercher "claude skills", "claude projects", "custom gpt", "creer un gpt", "gems gemini". Chaque feature = un article potentiel. Ex: "Claude Skills" = 1 800/mo KD 10.

   - **c) Tool usage keywords** : comment utiliser ces outils ("automatiser avec n8n", "creer un dashboard avec Make", "prompt engineering pour le marketing")

   - **d) Tool comparison keywords** : "[outil A] vs [outil B]", "[outil] gratuit ou payant", "[outil] alternative". Lion fait 4 700/mo avec "chatgpt gratuit ou payant".

   - **e) New tools / Newsjacking keywords** : les outils IA qui viennent de sortir ou qui buzzent. Strategie Ecole Cube : le premier a publier un guide prend la position. Scanner les 3-6 derniers mois et chercher : nouveaux outils de vibe coding (Lovable, Bolt, Windsurf, Cursor, v0, Firebase Studio...), nouveaux agents IA (OpenClaw, Devin, Replit Agent...), nouvelles features IA. Ex: "openclaw" = 13 000/mo KD 9, "lovable ai" = 9 200/mo KD 7, "windsurf ai" = 11 000/mo KD 16. Ces keywords ont un volume enorme, une concurrence faible, et si l'outil est utilise/enseigne dans les formations c'est un pont outil parfait. Meme si le pont est indirect (audience), le volume justifie l'article.

   - **f) Regulation & legal keywords** : si le programme mentionne RGPD, IA Act, conformite → rechercher "ia act", "rgpd ia", "rgpd chatgpt", "ia act entreprise", "conformite ia marketing". Ce sont des sujets que les ecoles concurrentes ne couvrent PAS (gap identifie). Ex: le programme IA Generative inclut "RGPD, IA Act" → article "IA Act : ce que les marketeurs doivent savoir en 2026".

   - **g) Concept keywords** : definitions et guides sur les concepts enseignes ("agent ia", "vibe coding", "growth hacking", "marketing automation", "funnel aarrr", "cro marketing", "ab testing", "llm"). Couvrir TOUS les concepts du programme, pas seulement les plus evidents.

   - **h) Method & framework keywords** : les methodes enseignees dans les formations ("ab testing", "cro", "funnel aarrr", "growth process", "experimentation marketing"). Ex: "ab testing" = 3 100/mo KD 7, "cro marketing" = 500/mo KD 0.

   - **i) Problem keywords** : ce que l'ICP cherche quand il a un probleme ("automatiser sa prospection", "scraping linkedin", "creer un chatbot", "landing page ia")

   - **j) Career keywords** : fiches metier et salaires ("growth marketing manager", "growth hacker salaire", "devenir growth marketer")

3. **FILTRE PERTINENCE — double logique de valeur**
   
   Chaque keyword doit etre evalue selon DEUX axes independants :
   
   **Axe 1 — "Est-ce que l'ICP va lire cet article ?"**
   L'ICP = marketeur avec 5-10 ans d'experience. Se demander : est-ce qu'un marketeur senior en poste ou en transition fait cette recherche ?
   - ✅ Direct : "ab testing", "chatgpt vs claude", "ia act", "agent ia marketing"
   - ✅ Probable : "llm c'est quoi" (un senior peut avoir du retard sur l'IA et vouloir rattraper), "rgpd chatgpt" (question pratique au bureau)
   - ❌ Non : "comment creer un site web" (trop debutant), "qu'est-ce que le marketing" (il sait deja), "cursor ai" (outil dev, pas marketeur)
   
   **Axe 2 — "Est-ce que cet article renforce le site ?"**
   Meme si l'ICP ne lit pas directement l'article, il peut avoir de la valeur pour :
   - **Autorite thematique** : Google voit qu'on couvre un sujet en profondeur → ameliore le ranking de TOUS les articles du cluster. "llm c'est quoi" renforce le cluster IA Generative qui aide les articles BOFU a ranker.
   - **Maillage interne** : l'article cree des liens internes vers les pages formations → ameliore le PageRank des LP.
   - **Domain Rating** : du contenu qui attire des backlinks naturels (definitions, guides de reference) → renforce le DR du site entier.
   
   **Regle de decision :**
   - ✅ ICP + Site → priorite maximale (ex: "ab testing", "chatgpt vs claude")
   - ✅ ICP seulement → priorite haute (ex: "agent ia marketing" — volume faible mais ultra pertinent)
   - ✅ Site seulement → garder si facile a produire (effort 3). Ex: "llm c'est quoi" (KD 0, facile, renforce le cluster). Ex: "vibe coding" (7 900/mo, KD 10, attire du trafic et des backlinks)
   - ❌ Ni ICP ni Site → rejeter (ex: "comment creer un site web", "cursor ai")
   
   **Ce filtre ne sert PAS a rejeter des articles faciles et utiles.** "LLM c'est quoi" = KD 0, effort 3 (facile), renforce le cluster IA, et un marketeur senior peut tout a fait le lire. On le garde. On rejette uniquement ce qui est vraiment hors sujet (pas de pont produit ET pas d'interet pour le site).

4. For each keyword, collect: volume (MARCHE FRANCAIS uniquement, verifier avec volume-by-country pour les keywords anglais), KD, CPC, current position (if any), intent type
5. Use Ahrefs tools (keywords-explorer-overview, keywords-explorer-volume-by-country pour les keywords anglais, site-explorer-organic-keywords, gsc-keywords)

5bis. **MOMENTUM CHECK — OBLIGATOIRE pour chaque keyword valide**

Le volume Ahrefs affiche une moyenne 12 mois — ca masque completement les tendances. Un keyword a 500/mo peut etre en pleine croissance (+80% sur 24 mois) ou en declin total (peak 2020, -60% depuis). On ne traite pas les deux de la meme facon.

**Process :**
- Pour chaque keyword qui passe le filtre pertinence, verifier la trajectoire sur 24 mois via `keywords-explorer-volume-history` (Ahrefs)
- En sanity check pour les keywords ambigus : cross-check Google Trends
- Classer en 3 buckets :

| Momentum | Critere | Action |
|---|---|---|
| ↗ **Growing** | Volume en hausse >30% sur 24 mois OU peak <6 mois | Prioriser (bonus scoring Phase 6) |
| → **Stable** | Variation ±30% sur 24 mois | OK, pas de bonus ni malus |
| ↘ **Declining** | Peak >18 mois en arriere OU baisse >30% sur 24 mois | Rejeter ou reformuler avec angle IA |

**Filtre "IA era" — applicable a 2026 :**

Question explicite a se poser pour chaque keyword : *"Est-ce que ce keyword a encore du sens a l'ere IA ?"*

Les sujets pre-IA (growth hacking pur, CRO classique, funnel AARRR sans IA, prospection manuelle, SEO old-school, split testing manuel) doivent soit :
- **Etre reformules avec l'angle IA** — ex: "CRO marketing" (peak 2019-2021) → "CRO IA : comment l'IA optimise les conversions en 2026"
- **Etre rattaches a un cluster IA plus large** (ex: AARRR dans un guide "Agent IA marketing")
- **Sinon : rejetes** ou traites comme reference historique TOFU uniquement

On ecrit pour 2026, pas pour 2020. Si un terme etait a la mode en 2019-2021 mais qu'aucun marketeur IA-first ne le cherche aujourd'hui, c'est un signal de declin meme si Ahrefs montre du volume residuel.

**Regle de rejet automatique :** peak >3 ans ET baisse >50% = obsolete = rejet sans appel.

6. **CROISEMENT ICP OBLIGATOIRE** — Pour chaque keyword, verifier dans `icp-bible.md` et `icp-messaging.md` :
   - Quel(s) persona(s) font cette recherche ? (P1 senior transition, P2 responsable stagne, P3 freelance, P4 CMO, P5 fondateur)
   - Est-ce lie a un declencheur d'achat documente ? (licenciement, echecs entretiens, prise de conscience IA, financement public disponible)
   - Est-ce lie a un pain point documente ? (marche sature, gap competences, obsolescence IA, syndrome generaliste)
   - Le keyword apparait-il dans les requetes de recherche listees dans icp-messaging.md ?
   
   Ne JAMAIS proposer un backlog sans la colonne "Personas" remplie pour chaque article. Un article qui ne sert aucun persona doit etre justifie par la valeur site (autorite thematique, backlinks).

**Deliver:**
- Keywords LP : liste pour optimisation des landing pages (pas du contenu blog)
- Keywords BLOG : clusters organises par produit et par type (tool / usage / comparison / concept / problem / career)
- Volume and difficulty for each cluster — **volumes FR verifies** (pour les keywords anglais, utiliser volume-by-country)
- Current positions (where we rank vs. where we don't)
- Gap analysis: "Product X = Y% of revenue but Z% of SEO coverage"
- **Pour chaque keyword : persona(s) servie(s) + declencheur/pain point ICP associe** — pas juste "ICP match oui/non"

---

### Phase 3 — Competitive Intelligence

**Before proposing articles, study what works for competitors.** Read `channels/seo/competitors.md` for the detailed analyses. Then check live data on the specific keywords you're targeting.

**Process:**
1. For each keyword cluster, check competitor positions using `site-explorer-organic-keywords`:
   - DataBird (data-bird.co)
   - Lion/Maria Schools (mariaschools.com)
   - Ecole Cube (ecole.cube.fr)
   - Le Wagon (lewagon.com) and other relevant competitors
2. Analyze what content type they use for each keyword
3. Identify opportunities: keywords where competitors are weak or absent

**Key questions to answer:**
- Who already ranks for our target keywords?
- What content type do they use? (tutoriel outil, comparatif, review, fiche metier)
- What's their DR vs ours? Can we realistically compete?
- Where are the gaps none of them cover?

**Deliver:**
- Competitive position map for each keyword cluster
- Content type used by each competitor per keyword
- Opportunities: keywords with weak or no competition
- Threats: keywords where a DR90+ site dominates

---

### Phase 4 — Map Existing Content

Before proposing anything new, understand what already exists. Read the SEO inventory (`channels-seo.md`) and cross-reference with live data.

**Process:**
1. List all existing articles/pages by theme
2. For each, note: current position, clicks, traffic value, date published, freshness
3. Classify by status:
   - **Protect** : ranke bien, contenu a jour → ne pas toucher
   - **Refresh** : ranke mais contenu date → mettre a jour (date, prix, outils, exemples)
   - **Abandon** : ranke sur un keyword sans produit correspondant → laisser en ligne mais ne plus investir
   - **Missing** : pas de contenu pour un keyword important → creer
4. Flag cannibalization (multiple pages sur le meme keyword)

**Deliver:**
- Coverage map by product
- Refresh candidates with URL, position actuelle, et ce qu'il faut changer
- Gaps by product (products with no content = highest priority)

---

### Phase 5 — Keywords to Articles (The Bridge Method)

C'est la phase critique. On passe de "mot-cle" a "article concret" en appliquant 4 filtres.

#### Filtre 1 : Valider la pertinence produit

- Ce keyword mene-t-il a un produit qu'on vend ?
- Le produit est le sujet principal (pont direct), un outil enseigne (pont outil), ou juste l'audience qui matche (pont audience) ?
- Si pont audience seulement : deprioritiser. Si aucun lien : supprimer.

#### Filtre 2 : Analyser l'intention de recherche (SERP)

Ne PAS deviner le format d'article. Regarder ce que Google ranke.

- Utiliser `serp-overview` (Ahrefs) ou le web pour voir les top 10 resultats
- Analyser :
  - Quel format domine ? (listicle, guide, comparatif, tutoriel, page produit)
  - Quel angle ? (debutant vs avance, pratique vs theorique)
  - Qui ranke ? (concurrents directs, medias, directories, YouTube)
  - Y a-t-il des PAA, featured snippets, AI Overviews ?
- Si le SERP ne montre QUE des pages produit/formation (ex: "formation marketing automation") → l'action est d'optimiser la LP, pas d'ecrire un article blog

#### Filtre 3 : Choisir le type de contenu

Basé sur l'analyse SERP et les patterns concurrents prouvés, choisir parmi **7 types d'articles** qui marchent sur le marché FR. Détail complet (pattern de titre, quand utiliser, pont produit, exemples concurrents avec volumes/positions) → [references/content-types.md](references/content-types.md).

Les 7 types : Tutoriel outil · Comparatif outils · Comparatif formations · Listicle outils · Fiche métier · Guide pratique · Définition.

⛔ **Règle anti-tool-first :** le choix du type se fait par keyword sur base SERP, pas "1 type par cluster dans l'abstrait". Un cluster JTBD contient typiquement plusieurs types (1 pillar long + 2-4 guides outils + 2-4 courts).

#### Filtre 4 : Formuler le titre et l'angle

Le titre doit :
1. **Contenir le keyword principal** (obligatoire)
2. **Utiliser une formule de titre prouvee** (voir ci-dessous)
3. **Indiquer clairement l'angle et ce qu'on va lire** — un titre vague comme "CRO marketing" ou "n8n vs Make" ne suffit PAS
4. **Se differencier** de ce que les concurrents proposent deja

**⚠️ REGLE ABSOLUE : ne JAMAIS utiliser un keyword brut comme titre d'article.** Le titre doit etre une phrase complete qui indique l'angle editorial. "automatisation marketing" n'est PAS un titre. "Automatisation marketing : par ou commencer en 2026" en est un.

**Formules de titres qui rankent** (données SERP réelles, marché FR 2025-2026) : **16 formules par type**, avec exemples position + trafic → [references/title-formulas.md](references/title-formulas.md).

**Comment choisir la bonne formule :**
1. Checker le SERP pour voir quelle formule domine dans le top 5
2. Si le SERP est vide : utiliser la formule la plus proche du type de contenu choisi (filtre 3)
3. Toujours ajouter un élément de différentiation : cible, année, ou angle unique (méthode complète, guide par catégorie)
4. Le titre doit promettre un résultat ou répondre à une question, pas juste nommer un sujet

#### Filtre 5 : Expansion en clusters (OBLIGATOIRE)

Quand un format ou un angle d'article fonctionne, **ne PAS s'arreter a un seul article**. Derouler systematiquement toutes les variantes. L'autorite thematique se construit par le volume de contenu sur un sujet, pas par un article isole.

**Regles d'expansion :**

1. **Expansion par outil** : si "prompt ChatGPT" est un bon keyword → derouler : "prompt Claude", "prompt Gemini", "prompt Midjourney", "meilleurs prompts marketing IA". Si "guide n8n" marche → "guide Make", "guide Zapier".

2. **Expansion par comparatif** : ne PAS faire un seul comparatif. Faire TOUS les comparatifs possibles entre les outils du meme cluster. Ex: n8n vs Make, Make vs Zapier, n8n vs Zapier, Zapier vs HubSpot workflows. Idem pour les IA : ChatGPT vs Claude, Claude vs Gemini, ChatGPT vs Gemini, etc.

3. **Expansion par angle** : un meme outil peut donner plusieurs articles. Ex pour n8n : guide complet, tutoriel debutant, 10 automatisations marketing, n8n vs Make, n8n pricing/gratuit ou payant, n8n pour le marketing.

4. **Expansion par sous-keyword** : quand on identifie un cluster porteur, creuser les variantes longue traine. Ex: "agent ia" → "agent ia marketing", "agent ia entreprise", "creer un agent ia", "agent ia c'est quoi", "meilleurs agents ia 2026".

5. **Ne PAS rejeter un keyword parce qu'un concurrent ranke dessus.** L'autorite thematique exige du volume. Si DataBird ranke sur "llm c'est quoi", ca ne veut pas dire qu'on ne doit pas le faire — au contraire, il FAUT le couvrir pour que Google nous considere comme une reference sur le sujet. La seule raison de rejeter : pas de pont produit OU piege d'intention SERP.

**Process d'expansion :**
- Pour chaque article valide par les filtres 1-4, se demander : "Quelles sont TOUTES les variantes possibles ?"
- Lister toutes les variantes (meme celles a volume plus faible)
- Verifier le volume/KD sur chaque variante via Ahrefs
- Garder toutes celles qui ont un pont produit, meme si le volume est faible (cluster building)
- Organiser les variantes en hub & spoke : 1 pillar page + N articles satellites

**Deliver:**
- Pour chaque keyword : article propose avec titre, type de contenu, pont produit, CTA, keywords secondaires
- **Clusters complets** : chaque format gagnant deroule en toutes ses variantes
- Keywords rejetes avec raison (rappel : "un concurrent ranke dessus" n'est PAS une raison valide)
- Type NEW ou REFRESH

---

### Phase 6 — Score, Prioritize & Build the Backlog

Scorer chaque article validé selon la grille complète (axes Product × Demand × Intent × Effort + ajustements + pénalités + mix longueur + mix formats) → [references/scoring-grid.md](references/scoring-grid.md).

**Résumé opérationnel :**

- **Base** : Product × Demand × Intent × Effort (max 81)
- **Ajustements** : First mover (+3), Refresh (+2), Trending fort (+3), Cluster (+1), Cross-sell (+1), Trending modéré (+1)
- **Pénalités** : DR mur (-3), Piège intent (-2), Declining (-2), Obsolète (-5 rejet)
- **Mix longueur obligatoire** : 30-40 % court (800-1 200 mots) / 30-40 % moyen (1 200-2 000) / 20-30 % long (2 000+)
- **Mix formats obligatoire** : aucun type >50 % du backlog. Diversité > score unitaire.

Si >40 % long-form → remplacer par du short-form à fort volume et KD faible. Dans chaque cluster JTBD : 1 pillar long + 3-4 moyens + 3-4 courts.

Validation de la phase : après scoring, lancer `gate_phase6(backlog)` depuis `pipeline/gates.py` (ou vérifier manuellement les invariants : mix longueur respecté, mix formats respecté, personas renseignées, pont produit explicite).

**Deliver:**
- Backlog score et classe (format tableau)
- **Tableau "Mix des formats"** montrant la repartition par type de contenu et les personas servies
- Organise par cluster produit ET par tier (S/A/B/C)
- Colonne Type (NEW / REFRESH) et URL existante si refresh
- **Colonne "Personas"** remplie pour chaque article
- Plan d'execution par phase avec timeline
- Save to `channels/seo/backlog.md`

---

### Phase 7 — Handoff to SEO Writer

Once the backlog is prioritized, hand off to the **seo-writer** skill for brief creation and article writing.

**Deliver:**
- Backlog priorise avec scores, pret a etre consomme par le skill `seo-writer`
- Pour chaque article, les informations necessaires au writer : keyword, volume, KD, type de contenu, pont produit, formation servie
- Recommandation sur les 3-5 premiers articles a rediger

> **Pour lancer la redaction :** Utiliser le skill `seo-writer` avec "Redige l'article #[numero]" ou "Redige l'article sur [keyword]".

---

## Output Format

A chaque phase, presenter les resultats clairement avant de passer a la suivante. Utiliser des tableaux, pas des murs de texte. Toujours relier au business impact.

**⚠️ Le livrable final est un DOCUMENT STRATEGIQUE, pas un rapport analytique.** Structure obligatoire :

**Page principale (actionnable, orientee decision) :**
1. Contexte (bref : probleme, opportunite, ICP)
2. Objectifs chiffres
3. Axes de travail (3-5 axes avec personas servies)
4. Backlog priorise avec calendrier (tableau avec titres COMPLETS des articles, pas les keywords bruts)
5. Mix des formats (tableau montrant la diversite)
6. Prochaines actions immediates

**Sous-pages (1 par article = 1 brief) :**
- Chaque article du backlog a sa propre page Notion
- Ne JAMAIS regrouper les briefs sur une seule page
- Chaque brief contient : keyword, volume, KD, SERP actuel, angle editorial, structure H1/H2, maillage interne, checklist qualite

**Sous-page annexe (donnees et analyses) :**
- Metriques domaine, evolution trafic, concurrents, content gap, SERP intelligence
- C'est le support analytique — PAS la premiere chose qu'on lit

Save the backlog to `channels/seo/backlog.md`.

Pour la redaction des articles (briefs 10x + ecriture), utiliser le skill **seo-writer**.

---

## Anti-Patterns (ne pas faire)

- **Ne JAMAIS recommander un keyword sans verifier le catalogue produit.** On a ete brule par "formation SEO", "formation prospection", "formation paid media" — aucun de ces produits n'existe. Lire `formations.md` avant toute recommandation.
- **Ne JAMAIS sauter de keyword a article sans checker le SERP.** Le SERP revele le format et l'angle que Google recompense. Deviner mene a du contenu qui ne ranke pas. Exemple : "formation marketing automation" → le SERP ne montre QUE des pages produit, pas d'articles blog.
- **Ne JAMAIS cibler un keyword piege.** "formation automatisation" est interprete par Google comme automatisme industriel (BTS, CODESYS), pas no-code. Toujours verifier le SERP avant de recommander.
- **Ne pas confondre volume et valeur.** Un keyword 50/mo BOFU KD 0 convertit mieux qu'un keyword 5 000/mo TOFU KD 30.
- **Ne pas creer de contenu "aussi bien" que les concurrents.** Si on ne peut pas faire 10x mieux, trouver un angle different ou skipper le keyword.
- **Ne pas proposer 50 articles sans plan d'execution.** Un backlog sans phases, effort, et tracking = une wish list.
- **Ne pas refresher du contenu qui mene a un produit qu'on ne vend pas.** Les vieux comparatifs (prospection, SEO, paid) restent en ligne mais ne recoivent plus d'investissement.
- **Ne pas ignorer les concurrents.** Avant de proposer un article, verifier si DataBird, Lion, ou Ecole Cube rankent deja dessus et avec quel type de contenu. Lire `channels/seo/competitors.md`.
- **Ne pas oublier le pont produit.** Chaque article doit avoir un pont explicite vers un produit {{COMPANY}}. "Cet outil est enseigne dans notre formation X" ou "{{COMPANY}} est dans ce comparatif". Si le pont n'existe pas, l'article ne convertira pas.
- **Ne JAMAIS s'arreter a un seul article quand un format marche.** Si "prompt ChatGPT" est pertinent, alors "prompt Claude", "prompt Gemini", "prompts marketing IA" le sont aussi. Derouler TOUTES les variantes. Un cluster = 5-10 articles, pas 1.
- **Ne JAMAIS rejeter un keyword parce qu'un concurrent ranke dessus.** L'autorite thematique se construit par le volume. Si DataBird est pos 5 sur "llm definition", ca veut dire que le keyword est valide, pas qu'il faut l'eviter. La seule raison de rejeter : pas de pont produit OU piege d'intention SERP.
- **Ne JAMAIS cibler un keyword en declin sans reformulation IA.** On ecrit pour 2026, pas pour 2020. Le volume Ahrefs est une moyenne 12 mois qui masque les tendances. Un keyword peut afficher 500/mo tout en ayant peake en 2019-2021 et decline de -60% depuis. Avant d'ajouter un keyword au backlog, verifier la trajectoire via `keywords-explorer-volume-history`. Si peak >18 mois et baisse >30% → reformuler avec angle IA ou rejeter. Si peak >3 ans et baisse >50% → rejet automatique. Exemples de termes a auditer systematiquement : "CRO marketing", "growth hacking" pur, "funnel AARRR", "split testing", "inbound marketing".
- **Ne JAMAIS cibler un keyword pre-IA sans pont IA.** Les marketeurs cherchent aujourd'hui "CRO IA", "optimisation conversions IA", "automatisation IA". Un article "CRO marketing" en 2026 sans mention d'IA = contenu qui se positionne comme old-school. Soit on reformule l'angle (CRO + IA), soit on ne fait pas l'article.
- **Ne JAMAIS construire un backlog tool-first.** 1 cluster = 1 outil (Claude, n8n, NotebookLM...) = erreur classique. Un marketeur ne cherche pas un outil a froid — il cherche a resoudre un probleme metier ("comment faire ma veille"). Le clustering doit etre **JTBD-first** : 1 cluster = 1 probleme metier (veille, reporting, choix d'outil, creation de decks, production de contenu, prospection, analyse, automatisation, strategie, onboarding equipe IA, GEO/AEO). Les outils entrent dans le cluster comme solutions au JTBD.
- **Ne JAMAIS produire 80% de long-form.** Un backlog domine par des "guides complets" 2 000+ mots bloque la velocity et surestime l'effort. Lion fait 4 705 visites/mo avec UN seul article court de 800 mots ("ChatGPT gratuit ou payant"). Viser 30-40% court / 30-40% moyen / 20-30% long. Dans chaque cluster JTBD : 1 pillar long + 3-4 moyens + 3-4 courts.

---

## Context files reference

| Fichier | Contenu | Quand le lire |
|---------|---------|---------------|
| `formations.md` | Catalogue produit (4 formations, prix, modules, URLs) | TOUJOURS — c'est le filtre produit |
| `product-marketing-context.md` | Contexte global + pointeurs vers tous les autres fichiers | TOUJOURS en premier |
| `icp-bible.md` | Data ICP de 565 appels (personas, triggers, objections) | Phase 1, Phase 7 (donnees proprietaires) |
| `icp-messaging.md` | Messaging par persona x canal | Phase 5 (angles d'articles), Phase 7 (hooks) |
| `channels-seo.md` | Inventaire blog existant (articles, positions, clics) | Phase 4 (cartographie existant) |
| `channels.md` | Performance canaux (536 deals, ROAS) | Phase 1 (objectifs) |
| `competitors-seo.md` | Analyses SEO detaillees des concurrents | Phase 3, Phase 5 (types d'articles) |
| `seo-backlog.md` | Backlog priorise courant | TOUJOURS — build on it |
| `voice-tone.md` | Ton editorial | Phase 7 (brief redaction) |

---

## Related Skills

- **seo-writer** : Redaction d'articles SEO a partir des briefs produits ici
- **seo-audit** : Audit technique et on-page
- **ai-seo** : Optimisation pour les moteurs de recherche IA (ChatGPT, Perplexity, AI Overviews)
- **content-strategy** : Strategie de contenu plus large (pas seulement SEO)
- **programmatic-seo** : Pages SEO a l'echelle
