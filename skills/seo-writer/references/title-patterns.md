# Title patterns (references for seo-writer)

Source consolidée : SKILL.md Step 3bis/4 + [brain/editorial-guide.md](../../../brain/editorial-guide.md) §3.

Chargé à la demande quand le skill génère un titre.

## Règle de sélection (5 variantes scorées)

Générer 5 variantes de titre en interne, les scorer, sélectionner la meilleure automatiquement. Documenter le raisonnement dans le brief. Le client override après coup si besoin.

### 4 sources d'inspiration à croiser

1. **Pattern {{COMPANY}}** du type d'article (A-H ci-dessous) — base structurelle
2. **SERP Google top 10** sur le keyword — patterns validés par le marché (via Ahrefs `serp-overview` ou WebFetch)
3. **SERP YouTube** sur le même keyword — formules teaser optimisées CTR par créateurs pro
4. **Sources client** (transcripts, notes) — tournures exactes à reprendre

### Contraintes de construction

- Au moins 1 variante conforme au Pattern {{COMPANY}} du type
- Au moins 1 reprenant une formule validée par la SERP Google/YouTube
- Au moins 1 reprenant une tournure exacte des sources client (si fournies)
- Au moins 1 SEO-agressif (keywords secondaires, noms concurrents si pertinent)
- Toutes ≤ 70 caractères (exception si SEO compense)
- Toutes : action verb > descriptive verb

### Grille de scoring

| Critère | Poids | Barème |
|---|---|---|
| Keyword principal présent | 3 | 0/1 — obligatoire sauf exception |
| Action verb en tête ou proche | 2 | 0/1 |
| Keywords secondaires / concurrents nommés | 2 | 0 à 3 (max 3 sinon verbeux) |
| Pattern {{COMPANY}} du type d'article appliqué | 2 | 0/1 |
| Signal format explicite ([Guide complet], chiffre) | 1 | 0/1 |
| Tournure reprise des sources client | 1 | 0/1 — ne pas forcer |
| **Longueur ≤ 60 chars** | **2** | **0/1** — poids renforcé (tronqué en SERP au-delà) |
| Concision / clarté (pas de jargon inutile) | 2 | 0/1 |
| Ordre naturel des concurrents (notoriété lecteur) | 1 | 0/1 |
| Teaser fort (chiffre, dilemme, verbe puissant) | 2 | 0/1 |

**Égalité de score** : privilégier le plus **court** et le plus **simple**. 60 chars clair bat 74 chars technique.

## Patterns validés par type d'article

### 🔧 Pattern A — Tool guide (nom d'outil connu)

Format : `[Nom outil] : [Action verb] son [sujet] avec [nom outil] [Guide complet]`

Le nom d'outil en **première position** (recognition + SEO).

- ✅ `n8n : Automatiser son marketing avec n8n [Guide complet]`
- ✅ `Lovable : créer une landing page avec l'IA [Guide complet]`
- ❌ `n8n pour les marketeurs : le guide complet pour automatiser son marketing` (nom outil noyé)
- ❌ `Le guide complet pour automatiser avec n8n` (nom outil trop loin)

### 🎯 Pattern B — Pillar JTBD (job-to-be-done)

Format : `[Action verb] son [sujet métier] avec l'IA : la méthode en N étapes`

- ✅ `Automatiser son reporting marketing avec l'IA : la méthode en 4 étapes`
- ✅ `Automatiser sa veille marketing avec l'IA : la méthode en 4 étapes`
- ✅ `Scaler sa prospection B2B avec l'IA : la méthode complète en 2026`
- ❌ `Comment faire son reporting marketing` (verbe mou)

### ⚔️ Pattern C — Comparatif outils "X vs Y"

Format : `[A] vs [B] : quel [catégorie] choisir en [année]`

**Neutre et direct.** Pas de "match honnête" / "vrai comparatif" (marketing forcé).

- ✅ `n8n vs Make : quel outil d'automatisation choisir en 2026`
- ✅ `Claude vs ChatGPT : quelle IA choisir pour le marketing en 2026`
- ❌ `n8n ou Make : le match honnête pour les marketeurs`
- ❌ `n8n vs Make : le vrai comparatif sans langue de bois`

### 📋 Pattern D — Listicle proof-based

Format : `[N chiffre précis non-arrondi] [sujet] testés : [qualifieur impact]`

- ✅ `47 prompts ChatGPT marketing testés : ceux qui marchent vraiment en 2026`
- ✅ `12 workflows n8n testés pour automatiser son marketing`
- ❌ `Les meilleurs prompts ChatGPT pour le marketing` (trop vague)
- ❌ `50 prompts ChatGPT pour le marketing` (chiffre arrondi)

### 💼 Pattern E — Fiche métier

Format : `[Métier] : fiche métier, salaire et compétences en [année]`

**Ne pas confondre** avec article méthode/reconversion. Un article = un intent.

- ✅ `Prompt Engineer : fiche métier, salaire et compétences en 2026` (fiche)
- ✅ `Devenir Prompt Engineer en 2026 : méthode de reconversion en 6 étapes` (méthode, SÉPARÉ)
- ❌ `Devenir Prompt Engineer en 2026 : salaire (62 K€), compétences` (mélange)

### 🤖 Pattern F — Feature guide IA (Claude Skills, GPTs, Gems…)

Format : `[Nom feature] : créer des agents IA [sujet] sur mesure`

Vocabulaire : **"agents IA" > "assistants IA"** (tendance 2026). Pas de métaphores risquées ("stagiaire", "collègue").

- ✅ `Claude Skills : créer des agents IA marketing sur mesure`
- ✅ `GPTs : créer des agents IA marketing pour son équipe`
- ❌ `Transformer Claude en stagiaire marketing` (métaphore risquée)
- ❌ `Claude Skills : créer des assistants marketing sur mesure` ("assistants" daté)

### 💶 Pattern G — Comparatif prix "gratuit ou payant"

Format : `[Outil] : gratuit ou payant pour un [persona] en [année]`

Ton **neutre**. La provocation chiffrée ("240 € de gaspillage") peut exister mais dans un article séparé sur un tier premium.

- ✅ `ChatGPT : gratuit ou payant pour un marketeur en 2026`
- ✅ `ChatGPT Max à 200 €/mois : gaspillage ou investissement pour les marketeurs` (article séparé)
- ❌ `ChatGPT Plus à 240 €/an : gaspillage ou investissement` (mélange les 2)

### 🧭 Pattern H — Pillar concept / outcome (GEO, AEO, LLM…)

Format : `[Concept keyword] : [bénéfice outcome] en [année] [Guide complet]`

**Toujours un bénéfice outcome concret**, pas une définition pure.

- ✅ `GEO : devenir la référence de ChatGPT en 2026 [Guide complet]`
- ✅ `AEO : capter les réponses directes dans les IA en 2026 [Guide complet]`
- ❌ `GEO : le guide complet du Generative Engine Optimization en 2026` (définition)
- ❌ `Qu'est-ce que le GEO en 2026 ?` (définition pure)

## Règle transverse — crochets `[Guide complet]` / `[Méthode]` / `[Fiche métier]`

Utiliser pour signaler le **format de contenu** en fin de titre, quand pertinent (tool guides, pillars concepts). Pas pour les comparatifs ou listicles chiffrés (qui se suffisent).

## Règle verbe — action vs descriptif

| ❌ Descriptif (mou) | ✅ Action (fort) |
|---|---|
| Comment faire sa veille | **Automatiser** sa veille |
| Comprendre ChatGPT | **Maîtriser** ChatGPT |
| Améliorer son SEO | **Doubler** son trafic SEO |
| Utiliser Claude | **Déployer** Claude dans son équipe |
| Apprendre le growth | **Passer** au growth |
| Découvrir les agents IA | **Construire** son premier agent IA |
| Analyser ses concurrents | **Décoder** la stratégie des concurrents |
| Écrire avec l'IA | **Produire** 10x plus avec l'IA |

**Verbes qui marchent en marketing/IA** : automatiser, maîtriser, déployer, construire, décoder, doubler, diviser par X, produire, scaler, passer à, basculer vers, transformer, orchestrer, industrialiser.

## H1 vs title SEO

- **Title** (balise `<title>`) : ce qu'affiche Google en SERP. 50-60 chars. Action-verb loaded.
- **H1** : titre sur la page. Peut être plus long, plus bénéfice-loaded. Souvent identique au title ou légèrement enrichi.

## Slug

- 3-5 mots max
- Sans filler words (comment, le, la, de, avec)
- **Jamais d'année** (doit pouvoir refresh sans changer l'URL)
- Pas d'accents, dashes uniquement

Exemples :
- ❌ `/blog/comment-faire-sa-veille-marketing-avec-ia-2026`
- ✅ `/blog/automatiser-veille-marketing-ia`
