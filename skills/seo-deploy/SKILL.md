---
name: seo-deploy
description: >
  Déploie un article SEO finalisé sur le CMS Webflow en brouillon, orchestre l'indexation GSC
  après publication humaine, et capture les corrections faites par l'humain pour améliorer
  la rédaction future (learning loop).
  Triggers : "déploie sur webflow", "push webflow", "envoie en brouillon", "publie le draft",
  "article prêt à déployer", "indexation gsc", "soumettre à l'indexation",
  "apprends des corrections", "remonte les diffs", "capture les corrections humaines",
  "article publié par [nom] récupère les changements".
  Pour la rédaction, voir seo-writer. Pour l'indexation GSC technique seule, voir seo-google.
metadata:
  version: 1.2.0
  inputs:
    article: "path vers l'article markdown finalisé (Phase A)"
    published_url: "URL publique de l'article publié (Phase B)"
    edited_article: "path vers la version corrigée humaine (Phase C)"
  scripts:
    - scripts/drive_push.py   # Phase A (DÉFAUT) — dépôt Google Doc sur Drive, routage publié/draft auto
    - scripts/pre_flight.py   # Phase A Step 1 — orchestrateur des 7 checks seo-writer + frontmatter + FAQ
    - scripts/analyze_article_diff.py   # Phase C Step 2 — diff metrics skill vs édité humain
  lib:
    - lib/webflow_deploy.py   # push Webflow + upload assets + génération images + drift check (v1.2)
    - lib/preview_article.py  # preview local HTML avant push
---

## Calibration (à faire avant le premier usage)

Ce skill porte une méthode. Il lui manque votre contexte. Renseignez :

| À remplir | Où |
|---|---|
| Votre CMS et ses identifiants | `.env`, et adapter `lib/` si vous n'êtes pas sur Webflow |
| Vos catégories de blog | `lib/webflow_deploy.py`, dictionnaire de catégories |
| Votre charte d'aperçu | `lib/preview_article.py`, bloc CSS |

> Ce skill a été construit sur Webflow. La méthode (aperçu local, contrôle avant publication, vérification
> après coup) vaut pour tout CMS ; le client d'API est à réécrire pour le vôtre.

Tant que ces cases sont vides, le résultat sera correct dans la forme et creux sur le fond.

# SEO Deploy

You are a deployment and learning specialist. Ton rôle : prendre un article validé par l'humain, le déposer de façon fiable, déclencher l'indexation GSC une fois publié, et capturer les améliorations faites par l'humain pour enrichir le skill de rédaction.

## ⚠️ Chemin de dépôt par défaut : Google Drive (depuis juin 2026)

Le push Webflow direct (`lib/webflow_deploy.py`) est **instable** : Webflow Rich Text V2 strippe les `<ol>` numérotés, a perdu des sections entières (bug confirmé sur `claude-skills-marketing`, section Ressources avalée), et le push échoue/bug fréquemment. **On ne déploie plus en automatique vers Webflow.**

**Workflow par défaut : déposer l'article en Google Doc sur Drive** via `scripts/drive_push.py` :
- `python3 scripts/drive_push.py` → route auto : publié (statut Webflow) → dossier **Publiés**, draft → dossier **IA SEO**.
- `python3 scripts/drive_push.py --dump` → tout dans **IA SEO**, tri manuel ensuite.
- Auth : `GOOGLE_DRIVE_REFRESH_TOKEN` (scope `drive`) + client OAuth des Ads, dans `.env`. Dossiers cibles : `GOOGLE_DRIVE_FOLDER_DRAFTS` / `GOOGLE_DRIVE_FOLDER_PUBLISHED` dans `.env`. Fidélité exacte, sans copier-coller.

**Webflow reste la cible de publication LIVE** (le blog tourne dessus), mais la mise en ligne se fait **à la main** depuis le Doc Drive validé, pas via le push buggé. Les Phases A (push Webflow draft) ci-dessous sont **dépréciées / secours** tant que les bugs Rich Text ne sont pas réglés. Le bug `<ol>` a un workaround (conversion `<ol>`→`<ul>` numéroté manuel dans `prepare_payload.py`), mais la perte de sections n'est pas résolue → Drive reste plus sûr.

## Principe : validation humaine entre chaque phase

Ce skill NE publie JAMAIS tout seul. Il fonctionne en 3 phases, chacune déclenchée par l'humain :

| Phase | Trigger humain | Action | Sortie |
|---|---|---|---|
| **A — Push brouillon** | "déploie sur webflow", "push en brouillon" | Validation finale + push CMS Webflow en **DRAFT** | URL du brouillon Webflow |
| **B — Indexation** | "article publié, lance l'indexation" | Soumission de l'URL à GSC Indexing API | Status d'indexation |
| **C — Learning loop** | "remonte les diffs", "apprends de la version finale" | Fetch version publiée, diff avec brouillon, append au fichier d'apprentissage | Résumé des patterns appris |

**Règle absolue : jamais passer de phase A à phase B sans confirmation humaine explicite que l'article est publié.** Le skill n'a pas de vision sur le workflow éditorial interne {{COMPANY}} — c'est l'humain qui tranche.

---

## Before Starting — Context to load

1. Read `brain/product-marketing-context.md` (liens, catalogues formations)
2. Read `channels/seo/backlog.md` (pour retrouver le brief de l'article, sa position dans le calendrier)
3. Read `memory/MEMORY.md` (auto-chargé par Claude Code) — index des feedbacks accumulés par thème. `seo-writer` et `seo-deploy` chargent les feedbacks pertinents à la demande via ce hub.
4. Read `memory/webflow_config.md` si existant — IDs site, collection, champs CMS déjà résolus

**Inputs attendus pour Phase A :**
- Un fichier markdown dans `content/blog/[slug].md` validé (a passé le self-check `seo-writer`)
- Title SEO, slug, meta description, keywords extractibles du frontmatter
- Confirmation humaine explicite : "déploie l'article [slug]"

---

## Phase 0 — Preview local avant Webflow

Avant tout push Webflow, générer un preview HTML local de l'article et l'ouvrir dans le navigateur du client pour revue. Ça évite des allers-retours Webflow inutiles et permet de corriger le contenu avant qu'il touche le CMS.

```python
from preview_article import preview_article
preview_article("content/blog/nom-article.md")
# → génère /tmp/{{SLUG}}-preview/[slug].html + ouvre dans le navigateur
```

Le preview rend l'article avec la charte de marque (Oswald + Inter, cream + navy), inline les SVG schémas présents localement, affiche la metadata frontmatter dans un encadré, et simule l'apparence future de la page blog.

**Trigger humain** : "preview l'article [slug]" ou "prévisualise avant Webflow".

**Quand valider ce preview** : l'humain relit, corrige si besoin dans le markdown, et valide verbalement ("OK envoie sur Webflow") avant que le skill passe à Phase A.

## Phase A — Push en brouillon Webflow

Vue d'ensemble de Phase A :

```
A.1 Pre-flight check ─────────┐
A.2 Résoudre config Webflow   │
A.3 Générer les images        │
    ├─ Nano Banana (photos)   │
    └─ Claude SVG (schémas)   │
A.4 Upload assets Webflow     │
A.5 Markdown → HTML + inject  │
A.6 Drift check Webflow       │  (NOUVEAU v1.2 — GATE OBLIGATOIRE)
A.7 Créer/PATCH item DRAFT    │
A.8 Retour au valideur        ┘
```

### Step 1 — Pre-flight check (obligatoire avant tout push)

Lancer le script orchestrateur :

```bash
python3 skills/seo-deploy/scripts/pre_flight.py <article.md>
```

Le script exécute :
- Frontmatter complet (Title SEO, Slug, Meta description, Keyword principal, Auteur)
- Section FAQ présente (min 3 questions)
- Les 7 checks `seo-writer` : `check_voice`, `check_meta`, `check_title`, `check_links`, `check_facts`, `check_rhythm`, `check_hook`

Si le script retourne exit code ≠ 0 → **arrêt**, reporter les issues à l'humain, renvoyer vers `seo-writer` ou correction manuelle. **Ne rien pusher** tant que tous les checks ne passent pas, OU que l'humain override explicitement après revue.

### Step 2 — Résoudre la config Webflow (si pas déjà en mémoire)

À la première utilisation, identifier :

1. **Site ID {{COMPANY}}** via `data_sites_tool` (lister les sites → prendre celui correspondant à {{DOMAIN}})
2. **Collection "Blog"** via `data_cms_tool` (lister les collections du site → prendre "Blog" ou équivalent)
3. **Schéma des champs CMS** : name, slug, post-body (rich text), summary (meta description), main-image, author, published-on, seo-title, seo-meta-description, etc.

**Sauvegarder dans `memory/webflow_config.md`** pour éviter de re-résoudre à chaque push :

```markdown
# Webflow config — {{COMPANY}}

- **Site ID** : [uuid]
- **Site domain** : {{DOMAIN}} (ou webflow staging)
- **Collection "Blog"** :
  - ID : [uuid]
  - Mapping champs markdown → Webflow :
    - `title` (markdown H1) → `name` (Webflow)
    - `slug` (frontmatter) → `slug`
    - `meta description` → `seo-meta-description` + `summary`
    - `title SEO` → `seo-title`
    - corps (markdown body) → `post-body` (rich text HTML)
    - auteur → `author` (référence vers collection Authors si existe)
    - date publication → `published-on`
- **Auteur par défaut** : {{OWNER}} Gabriel (ID : [uuid])
```

### Step 3 — Transformer markdown → Webflow Rich Text

Webflow Rich Text attend du HTML. Conversion minimale à faire :

| Markdown | Webflow Rich Text HTML |
|---|---|
| `# H1` | ⚠️ **NE PAS inclure le H1 dans le body** — il est dans le champ `name` |
| `## H2` | `<h2>...</h2>` |
| `### H3` | `<h3>...</h3>` |
| `**bold**` | `<strong>...</strong>` |
| `*italic*` | `<em>...</em>` |
| `- liste` | `<ul><li>...</li></ul>` |
| `1. liste` | `<ol><li>...</li></ol>` |
| `[texte](url)` | `<a href="url">texte</a>` |
| `> citation` | `<blockquote><p>...</p></blockquote>` |
| `` `code` `` | `<code>...</code>` |
| `| table \| html |` | `<table><tr><td>...</td></tr></table>` |
| `[IMAGE: desc]` | **Garder comme bloc spécial** (voir ci-dessous) |
| `---` | `<hr>` |

**Gestion des images (v1.2 — Claude SVG prioritaire) :**

Pipeline intégré via la lib `skills/seo-deploy/lib/webflow_deploy.py`. **PAR DÉFAUT : Claude SVG.** Nano Banana est l'exception.

| Placeholder markdown | Générateur | Output | Usage | Fréquence |
|---|---|---|---|---|
| `[IMAGE-SCHEMA: description]` | **Claude SVG** (code direct) | SVG | Concepts, process, questionnements, diagrammes, graphiques, comparatifs conceptuels, arbres de décision, quadrants, métaphores visuelles | **≥ 95% des cas** |
| `[IMAGE-PHOTO: description]` | **Nano Banana Pro** (Gemini) | JPEG | **Uniquement** photo-réalisme pur : portraits, paysages, scènes naturalistes, captures de vraie vie | Exceptionnel (< 5%) |
| `[IMAGE: description]` (legacy) | Default → SCHEMA Claude SVG | SVG | Transition (toujours SVG sauf contre-indication explicite) | Fallback |

**⚠️ Règle absolue** : si tu hésites entre SCHEMA et PHOTO, c'est un SCHEMA. Nano Banana ne sert QUE quand on veut représenter quelque chose qui existe physiquement dans le monde réel (visage humain, paysage, objet photographié). Pour tout concept abstrait, process, relation, comparaison, hiérarchie, flux d'information → Claude SVG.

**Le rôle du SVG {{COMPANY}} n'est PAS de faire joli, c'est de FAIRE COMPRENDRE.** Un schéma doit illustrer un concept du texte que l'humain visualise mieux en image qu'en mots. Si le SVG peut être remplacé par un paragraphe sans perte d'info, c'est un mauvais SVG.

**Types de schémas à privilégier (ordre de puissance pédagogique) :**

1. **Process flow** : étapes successives (sourcer → collecter → synthétiser → diffuser)
2. **Arbre de décision** : "si X alors Y" avec branches
3. **Quadrant 2×2** : 2 axes, 4 zones + objets placés dans les zones
4. **Diagramme conceptuel** : blocs + relations + flèches
5. **Before/After chiffré** : 2h47 → 23 min avec flèche
6. **Hub & spoke** : centre + satellites
7. **Comparatif conceptuel** : 2 philosophies face à face avec leurs caractéristiques
8. **Timeline** : évolution dans le temps

**À NE PAS FAIRE en SVG** :
- Un tableau stylisé (c'est une table HTML déguisée, pas un dessin)
- Une liste à puces colorée (même problème)
- Un simple texte dans une box (inutile)

**Charte visuelle obligatoire** : toutes les images (photo et SVG) doivent respecter `brain/design-system.md` :
- Dominant : cream `#FAF9F5` + navy `#282C4B` / `#394E8A`
- Accents royal blue `#103ACD` + mustard `#EFC222` **uniquement sur détails ponctuels** (≤ 5 % surface)
- Pas d'emerald/coral, pas de 3D futuristic, pas de stock SaaS

**Direction artistique Nano Banana** : le wrapper `NanoBananaGenerator.brand_prompt_wrapper()` injecte automatiquement la palette + les règles anti-stock + les exclusions (no text, no faces). L'appelant fournit juste la **scène** concrète.

**Design SVG** : Claude génère directement le XML SVG à partir des 6 patterns de `design-system.md` (process flow, comparison split, quadrant, scorecard, before/after, hub & spoke). Font : Oswald (titres) + Inter (body).

### Step 3bis — Génération et upload des images (v1.1)

```python
from webflow_deploy import WebflowDeployer, NanoBananaGenerator, extract_image_placeholders

# 1. Parser le markdown pour extraire les placeholders
placeholders = extract_image_placeholders(markdown_text)

# 2. Pour chaque placeholder, générer l'image
deployer = WebflowDeployer()
generator = NanoBananaGenerator()

for p in placeholders:
    if p.kind == "photo":
        path, mime, _ = generator.generate(p.description, f"content/images/{slug}/{slug}-{p.index}.jpg")
    else:  # schema
        # Claude écrit directement un SVG basé sur description + data
        svg = build_svg_from_description(p)  # voir patterns dans design-system.md
        path = f"content/images/{slug}/{slug}-{p.index}.svg"
        pathlib.Path(path).write_text(svg)
        mime = "image/svg+xml"

    # 3. Upload sur Webflow
    asset_id, hosted_url = deployer.upload_asset(path, f"{slug}-{p.index}.{ext}", mime, p.alt_text)

    # 4. Remplacer le placeholder dans le HTML généré
    html = deployer.replace_placeholder(html, placeholder_regex_for(p), hosted_url, p.alt_text)

# 5. Le premier placeholder photo devient aussi la featured image
if any(p.kind == "photo" for p in placeholders):
    first_photo = next(p for p in placeholders if p.kind == "photo")
    # L'asset_id correspondant va dans le champ 'blog-post-featured-image'
```

**Règle importante** : la première photo générée devient **automatiquement la featured image** du post (champ `blog-post-featured-image` Webflow), utilisée pour les partages sociaux et la card preview blog.

**Tolérance à l'échec** : si Nano Banana échoue (quota, erreur réseau), retry 1 fois puis skipper avec placeholder conservé (signal visuel orange au valideur humain) plutôt que tout bloquer.

### Step 3ter — Drift check Webflow (GATE OBLIGATOIRE, v1.2)

**Pourquoi** : un re-push aveugle écrase silencieusement les corrections humaines déjà appliquées sur Webflow. Le contenu live est la source de vérité tant que les corrections n'ont pas été rapatriées en local via Phase C.

**Quand** : à chaque run, **création comme PATCH**. Aucun bypass automatique.

**Procédure** :

1. **Lookup par slug** dans la collection Blog :
   ```python
   from webflow_deploy import WebflowDeployer
   existing = WebflowDeployer().find_item_by_slug(slug)
   ```

2. **Cas création** (l'humain pense créer un nouvel article) :
   - `existing is None` → pas de drift possible, on enchaîne sur Step 4 (création).
   - `existing is not None` → **STOP**. Un item avec ce slug existe déjà sur Webflow. Reporter : `⚠️ Slug "{slug}" déjà présent côté Webflow (item id, dernière modif). Tu confirmes vouloir écraser cette version ?` Exiger la phrase exacte `"écrase, j'ai vérifié"`.

3. **Cas PATCH** (item connu d'un run précédent) :
   - Toujours `existing is not None` ; faire la diff suivante avant le PATCH.

4. **Diff `post-body`** (et seulement `post-body` — on ignore name/slug/seo-title/meta-description) :
   ```python
   report = WebflowDeployer().diff_post_body(local_html, existing["fieldData"]["post-body"])
   ```
   Le helper retourne `{"drift": bool, "blocks_only_in_remote": [...], "blocks_changed": [...], "summary": "..."}`.

5. **Si `drift is False`** → continuer sur Step 4. Logger `[drift-check] OK — pas de divergence détectée`.

6. **Si `drift is True`** → **STOP**. Afficher au valideur :
   ```
   ⚠️ Drift détecté sur post-body Webflow vs version locale.

   Blocs présents UNIQUEMENT côté Webflow (potentielles corrections humaines à préserver) :
     - [extrait bloc 1, max 200 char]
     - ...

   Blocs modifiés (texte différent local ↔ Webflow) :
     - [extrait]
     - ...

   Deux options :
   (1) Tu as déjà fusionné ces corrections dans le markdown local et tu veux écraser → réponds exactement : "écrase, j'ai vérifié"
   (2) Tu veux d'abord rapatrier les corrections Webflow → on lance Phase C (learning loop) avant tout PATCH

   Sans la phrase exacte ci-dessus, je n'écris rien sur Webflow.
   ```

7. **Confirmation stricte** : la phrase doit être littéralement `"écrase, j'ai vérifié"` (insensible à la casse, espaces normalisés). Tout autre input ("oui", "ok", "vas-y", "confirme") = abandon. Pas de paraphrase tolérée — la friction est volontaire.

8. Logger la décision dans `memory/seo_publication_log.md` avec timestamp + slug + résultat (no-drift / overwrite-confirmed / aborted).

**Cas d'urgence où la lib ne peut pas joindre l'API Webflow** : ne pas pusher. Reporter l'erreur à l'humain. Le silence ≠ pas de drift.

### Step 4 — Créer l'item CMS en DRAFT (pas publié)

Via `data_cms_tool` (ou équivalent Webflow MCP), créer un item dans la collection Blog avec :

```
{
  "fields": {
    "name": "[Title SEO extrait du frontmatter]",
    "slug": "[slug extrait du frontmatter]",
    "seo-title": "[Title SEO]",
    "seo-meta-description": "[Meta description]",
    "summary": "[Meta description]",
    "post-body": "[HTML transformé]",
    "author": "[Author ID par défaut]",
    "published-on": null,
    "_draft": true,
    "_archived": false
  },
  "isDraft": true
}
```

**⚠️ Le flag `isDraft: true` est OBLIGATOIRE.** Jamais publier directement.

### Step 5 — Retourner le lien de preview au valideur humain

Après création réussie :

```markdown
✅ Brouillon créé sur Webflow.

**Article** : [Title]
**Slug** : /blog/[slug]
**URL brouillon (preview)** : [Webflow draft URL]
**Images à ajouter** : 3 placeholders signalés dans le texte (bloc orange "🖼️ IMAGE À AJOUTER")

**Prochaine étape (humain) :**
1. Ouvrir le brouillon Webflow
2. Ajouter/remplacer les 3 images
3. Review finale (vouvoiement, liens, mise en page)
4. Publier manuellement depuis Webflow
5. Me dire "article publié, lance l'indexation" pour Phase B

**Avant publication, pense à vérifier** :
- [ ] Featured image (hero) uploadée
- [ ] Cover image pour les partages sociaux (Open Graph)
- [ ] Catégorie(s) CMS sélectionnée(s)
- [ ] Tags éventuels
- [ ] Date de publication correcte
```

---

## Phase B — Indexation GSC après publication

**Triggered by explicit human confirmation :** "article publié, lance l'indexation" / "indexation gsc pour [slug]".

### Step 1 — Récupérer l'URL finale publiée

Deux cas :
- L'humain te donne l'URL directement → l'utiliser
- Sinon : `https://www.{{DOMAIN}}/blog/[slug]` (construction par défaut)

### Step 2 — Vérifier que l'URL est live

- Fetch la page via `WebFetch` → vérifier code 200 + contenu non vide
- Si 404 / redirection / page vide → STOP, demander à l'humain de vérifier

### Step 3 — Soumettre à l'indexation

**Déléguer au skill `seo-google`** pour utiliser l'API Indexing v3.

Instruction standard :
```
Soumettre [URL] à l'API Google Indexing v3, type URL_UPDATED.
Vérifier le status de la soumission (successful / rate limited / auth error).
```

Alternative si `seo-google` indisponible : guider l'humain pour un Submit manuel via GSC URL Inspection.

### Step 4 — Soumettre le sitemap (bonus)

Si le sitemap n'a pas été re-pingé récemment :
- Ping `https://www.google.com/ping?sitemap=https://www.{{DOMAIN}}/sitemap.xml`
- (Note : Google a déprécié le ping sitemap en 2023, mais c'est sans impact négatif. La vraie action = ajouter l'URL au sitemap + resubmit via GSC.)

### Step 5 — Log de publication

Ajouter une ligne au fichier `memory/seo_publication_log.md` :

```markdown
| Date publication | Slug | URL | KW principal | Status indexation | Position initiale (J+7) |
|---|---|---|---|---|---|
| 2026-04-27 | automatiser-veille-marketing-ia | https://www.{{DOMAIN}}/blog/automatiser-veille-marketing-ia | automatiser sa veille marketing | submitted | pending |
```

Planifier une relance J+7 pour vérifier l'indexation effective + la position initiale.

---

## Phase C — Learning loop : remontée des corrections humaines

**Triggered by :** "remonte les diffs", "apprends des corrections humaines sur [slug]", "capture les changements publiés".

C'est la phase la plus précieuse. L'humain a corrigé le brouillon en publiant — ces corrections contiennent les patterns de qualité que le skill `seo-writer` doit intégrer pour produire mieux la prochaine fois.

### Step 1 — Fetch la version publiée

- `WebFetch https://www.{{DOMAIN}}/blog/[slug]` (ou version canonique)
- Extraire le contenu principal (title, H1, H2s, corps, meta description si accessible)
- Sauvegarder en `content/blog/published/[slug]-published.md`

### Step 2 — Diff avec la version brouillon initiale

Lancer le script d'analyse :

```bash
python3 skills/seo-deploy/scripts/analyze_article_diff.py <skill.md> <edited.md>
```

Le script produit :
- Diff H2s (ajoutés / retirés)
- Diff liens (ajoutés / retirés)
- Delta metrics par dimension : word_count, paragraphs, pct_single_sentence_paragraphs, cadratins, anaphores, liens, etc.
- Option `--template` pour générer un squelette `feedback_<topic>.md` pré-rempli avec titre, meta et exemples avant/après

Ensuite, synthétiser manuellement les **patterns éditoriaux** réutilisables (pas juste la liste de modifs). Dimensions à analyser :

| Dimension | Questions à se poser |
|---|---|
| **Title** | Le titre a-t-il été modifié ? Pourquoi probablement ? (action verb changé, chiffre ajusté, audience recadrée) |
| **Intro** | L'intro a-t-elle été raccourcie/rallongée/réécrite ? Le hook element est-il resté ? |
| **H2s** | Quels H2 ont été reformulés ? Verbe d'action changé ? Chiffre ajouté ? |
| **Verbatims** | Y en a-t-il eu ajoutés/retirés ? |
| **Chiffres** | Des chiffres ont-ils été précisés, arrondis, ou sourcés différemment ? |
| **Tournures** | Phrases rallongées, asides ajoutés, métaphores changées ? |
| **CTAs** | Le CTA final a-t-il été modifié ? |
| **Longueur** | Gain/perte de X mots globalement ? Où ? |
| **Liens internes** | Lesquels ont été ajoutés/retirés ? |

### Step 3 — Extraire les patterns réutilisables

Ce qu'on cherche, ce n'est PAS "voici la liste de toutes les modifs". C'est "voici ce que j'aurais dû faire différemment au premier jet".

Exemples de patterns à capturer :
- ❌ "J'avais écrit 'les meilleurs prompts' → l'humain a remplacé par '47 prompts testés'" → **Pattern** : privilégier un chiffre précis + proof au lieu d'un superlatif
- ❌ "J'avais mis l'outil à la fin du titre → l'humain l'a mis en début" → **Pattern** : nom d'outil toujours en première position en tool guide
- ❌ "J'avais écrit une intro de 4 paragraphes → l'humain l'a condensée en 3" → **Pattern** : viser 120-150 mots max en intro

### Step 4 — Classer chaque pattern dans un fichier de feedback thématique

La mémoire longue n'est PAS un fichier monolithique. C'est un ensemble de `memory/feedback_<topic>.md` organisés par thème (convention validée sur 4+ learning loops) : un fichier = un thème cohérent = 1-5 règles liées.

Pour chaque pattern extrait du diff, identifier sa destination :

| Type de pattern | Destination |
|---|---|
| Règle de voix / narration stable | `brain/voice-tone.md` si structurel |
| Règle rédaction (intro, meta, titre, FAQ) | `memory/feedback_<aspect>.md` ciblé (ex: `feedback_meta_description.md`, `feedback_faq_trancher.md`, `feedback_ton_humble.md`) |
| Règle transverse éditoriale récurrente | `brain/editorial-guide.md` section pertinente |
| Pattern attrapable par script | Enrichir un script `skills/seo-writer/scripts/` existant ou en créer un nouveau |
| Stack / références / exemples produit | `memory/feedback_stack_<topic>.md` (ex: `feedback_stack_ia_canonique.md`) |
| Nouveau thème non classable | Nouveau `memory/feedback_<nouveau_topic>.md` |

Pour **chaque nouveau fichier de feedback créé**, ajouter un pointeur dans `memory/MEMORY.md` (section `### seo-writer` ou autre skill concerné). MEMORY.md est l'index auto-chargé par Claude Code à chaque session.

**Frontmatter standard des feedback files :**

```yaml
---
name: <titre court>
description: <résumé une ligne du pattern>
type: feedback
---
```

**Règles d'écriture :**
- Append à un feedback existant si le thème match ; sinon créer un nouveau fichier
- Un fichier = un thème cohérent, pas de fourre-tout
- Si un feedback dépasse 150 lignes, le splitter
- Chaque feedback documente : règle + why + how to apply + exemple corrigé (voir conventions existantes dans `memory/`)

### Step 5 — Propagation automatique via MEMORY.md

La propagation est **automatique** : `seo-writer` charge `memory/MEMORY.md` à chaque session (auto-chargé par Claude Code). MEMORY.md pointe vers tous les feedbacks pertinents ; le skill les lit à la demande selon le thème.

**Pas de consolidation trimestrielle imposée.** Quand un thème se stabilise (3+ feedbacks récurrents sur le même aspect), proposer à l'humain de migrer les règles vers le document canonique correspondant :

| Feedback memory stabilisé | Destination canonique |
|---|---|
| Règles rédaction éprouvées | `brain/editorial-guide.md` |
| Règles voix / ton stables | `brain/voice-tone.md` |
| Règles SEO (titre, meta, anti-patterns) | `skills/seo-writer/references/*.md` |
| Règles attrapables en script | Nouveau script `skills/seo-writer/scripts/` |

Les feedbacks memory restent le lieu d'**accumulation récente**. Les `agents/*.md` et `references/*.md` sont les lieux de **consolidation stabilisée**.

### Step 6 — Retour au valideur humain

```markdown
✅ Learning loop terminé pour [slug].

**Modifications humaines détectées** : X
**Patterns extraits et ajoutés au mémoire** : Y
**Dimensions touchées** : [title, intro, H2s, tournures, ...]

**Top 3 apprentissages** :
1. [Pattern le plus important]
2. ...
3. ...

Ces patterns seront lus automatiquement lors de la prochaine rédaction via `seo-writer`.
```

---

## Output Format

Selon la phase :

**Phase A** : confirmation création brouillon + URL preview + checklist pré-publication
**Phase B** : confirmation soumission GSC + prochaine vérif J+7
**Phase C** : résumé des patterns extraits + total cumulé dans le fichier learnings

---

## Anti-Patterns (ne pas faire)

- **Never publish directly.** Le skill pousse uniquement en DRAFT. La publication est une action humaine explicite. Si l'humain demande "publie" sans dire "brouillon", redemander la confirmation : "Je pousse en brouillon, tu valides et publies toi-même dans Webflow, correct ?"
- **Never skip the pre-flight check.** Article sans frontmatter complet, sans FAQ, ou avec du tutoiement = refus de push. Mieux vaut renvoyer au skill `seo-writer` que polluer le CMS.
- **Never push to Webflow without the drift check (Step 3ter).** Le check tourne sur création comme sur PATCH. En cas de divergence détectée, exiger la phrase littérale `"écrase, j'ai vérifié"` — tout autre input ("oui", "ok", "vas-y") = abandon. La friction est volontaire pour éviter d'écraser silencieusement des corrections humaines faites côté CMS (incident de référence : push du mardi qui a écrasé un article corrigé sur Webflow).
- **Never auto-trigger Phase B.** L'indexation ne se déclenche que sur confirmation humaine de publication. Sinon risque d'index une page 404.
- **Never overwrite an existing feedback memory file.** Toujours append à un `feedback_<topic>.md` existant si le thème match, ou créer un nouveau fichier ciblé. La mémoire longue se construit article par article, fichier par thème. Voir convention Phase C Step 4.
- **Never consolidate learnings without human approval.** L'option heavy (réécriture de `seo-writer/SKILL.md`) ne se fait jamais seul. Toujours proposer à l'humain d'abord.
- **Never commit images as broken links.** Si des placeholders images sont dans le brouillon, c'est OK (bloc orange visible). Mais jamais insérer une URL d'image cassée ou inventée.
- **Never touch live pages.** Phase B agit sur GSC (indexation), pas sur le contenu de la page. Si une correction est nécessaire après publication, c'est un nouveau cycle Phase A.
- **Never skip the learning loop.** C'est l'étape qui fait progresser la qualité. Si un humain dit "c'est publié" mais saute Phase C, proposer explicitement : "Tu veux que je remonte les diffs pour apprendre ?"

---

## Integrations avec les autres skills

| Skill | Quand l'utiliser | Comment |
|---|---|---|
| `seo-writer` | Produit l'article | Input de Phase A |
| `seo-strategy` | Fournit le brief | Référence pour les patterns métier |
| `seo-google` | Indexation Phase B | Délégation explicite |
| `seo-image-gen` | (V2) génération images auto | Remplacerait les placeholders avant Phase A |
| `seo-backlog` | Mise à jour statut article après publication | Append "✅ publié le [date]" au ligne du backlog |

---

## Questions ouvertes à résoudre au premier run

1. **Site Webflow {{COMPANY}}** : un seul site ou plusieurs (prod, staging) ? Résoudre via `data_sites_tool`.
2. **Collection "Blog"** : nom exact, ID, schema. Résoudre via `data_cms_tool`.
3. **Auteurs** : collection séparée "Authors" avec {{OWNER}} comme item, ou champ texte simple ?
4. **Catégories / Tags** : existent-ils comme collections séparées ? Comment les remplir ?
5. **Featured image / Open Graph image** : champs Webflow attendus + format (URL vs asset ID) ?
6. **Workflow de publication humain** : qui publie ? {{OWNER}} directement ou passage par un autre valideur ?
7. **GSC property** : le domaine exact enregistré dans GSC (www.{{DOMAIN}} vs {{DOMAIN}} vs blog.{{DOMAIN}}) ?
8. **Indexing API** : credentials déjà configurés ? Si non, voir avec `seo-google` pour le setup.

Ces questions doivent être clarifiées au premier usage et sauvegardées dans `memory/webflow_config.md` pour les runs suivants.
