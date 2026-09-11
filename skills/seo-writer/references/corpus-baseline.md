# Référence de corpus : des règles de style transformées en seuils mesurables

**L'idée, qui vaut pour n'importe quelle marque :** au lieu de décrire votre style avec des adjectifs
(« direct », « fragmenté »), vous mesurez vos meilleurs articles et vous en tirez des **seuils chiffrés**
qu'un script peut vérifier avant publication.

## Comment produire votre propre référence

1. Choisissez 5 à 8 articles qui représentent le mieux votre style. Idéalement ceux qui ont été relus
   et corrigés à la main, pas ceux produits à la chaîne.
2. Choisissez 2 ou 3 articles que vous jugez moins bons : ils servent de contraste.
3. Lancez `python3 skills/seo-writer/scripts/analyze_corpus.py` sur les deux groupes.
4. Reportez les résultats dans le tableau plus bas, et mettez à jour après chaque nouvel article
   qui entre dans le groupe de référence.

| Groupe | Vos articles | Usage |
|---|---|---|
| **Référence** | {{listez vos slugs}} | La cible |
| **Contraste** | {{listez vos slugs}} | Ce qu'il ne faut pas reproduire |
| **Paires avant/après édition** | {{un article brut et sa version éditée}} | Révèle la signature de l'édition humaine |

> Les valeurs ci-dessous viennent d'un corpus réel et servent d'**exemple de ce à quoi ressemble un bon
> résultat**. Recalculez les vôtres : un seuil emprunté à quelqu'un d'autre vous fait écrire comme lui.

## Règles mathématiques émergentes (seuils quantifiés)

Dérivées des p20-p80 du corpus référence. Thresholds à titre indicatif, pas à appliquer aveuglément (jugement éditorial prioritaire).

### Structure

| Métrique | Corpus référence (p20 - p80) | Seuil recommandé | Règle proposée |
|---|---|---|---|
| Word count | 1564 - 2372 | 1500-2500 mots | cible plage ; au-delà = check de la valeur ajoutée |
| H2 count | 7 - 11 | 6-11 | |
| avg_paragraph_words | 26 - 30 | ≤ 32 mots moyenne | Paragraphes longs = signal de rédaction non éditée |
| avg_sentence_words | 13.6 - 15.0 | 13-16 mots moyenne | Phrases courtes = voix de marque |
| **pct_single_sentence_paragraphs** | **21 - 53 %** | **≥ 30 %** | **Signature d'un rythme fragmenté** |

### SEO

| Métrique | Corpus référence (p20 - p80) | Seuil recommandé | Note |
|---|---|---|---|
| H1 length | 54 - 68 chars | 50-70 chars | Plage plus souple que le check actuel "≤ 60" |
| Meta length | 144 - 166 chars | 140-170 chars | **Plage plus souple que le 150-160 actuel** (voir Recos plus bas) |
| Internal blog links | 3 - 3 | **3-5** (actuel OK) | Confirmé |
| Liens vers l'offre | 2 - 4 | au moins 1 appel à l'action | Confirmé |
| External links | 7 - 16 | Pas de max strict | Les articles dense en sources ont 15+ liens externes |
| Image placeholders | 0 - 1 | **2-3 par 2000 mots** (actuel OK) | Le corpus montre que les articles publiés n'ont souvent pas les placeholders (captures ajoutées directement en Webflow) |

### Voix

| Métrique | Corpus référence (p20 - p80) | Corpus drift (médiane) | Seuil recommandé |
|---|---|---|---|
| **Cadratins / 1000 mots** | **0 - 4.6** | **17.8** | **< 5 / 1000 mots** (25x moins que drift) |
| Cadratins total | 0 - 7 | 23 | Max 1 acceptable hors H2 |
| Anaphoras (3+ paras same start) | 0 - 1 | 1 | **Pattern rare à activer plus** (voir Recos) |
| **pct_sentences_with_precise_numbers** | **12.7 - 21.2 %** | **14-23 %** | **Cible ≥ 15 %** (1 phrase sur 6+ contient un chiffre précis) |

### Intro

| Métrique | Corpus référence (p20 - p80) | Corpus drift (médiane) | Seuil recommandé |
|---|---|---|---|
| **hook_first_sentence_words** | **3 - 12 mots** | **15 mots** | **≤ 12 mots pour le hook** |
| **first_non_rounded_number_position** | **phrase #1 - #3** | phrase #1 | **≤ phrase #3** (chiffre précis tôt dans l'article) |

## Signature d'édition humaine (paires skill → edited)

Pattern ultra-stable sur les 2 paires analysées : **l'édition humaine fragmente TOUJOURS le rythme**.

| Article | % paras 1-phrase (skill) | % paras 1-phrase (edited) | Delta |
|---|---|---|---|
| claude-cowork-marketing | 40.7 % | 63.9 % | **+23 pts** |
| deployer-agent-seo-ia | 31.1 % | 52.6 % | **+21 pts** |

**Règle dérivée :** dès la rédaction, viser **≥ 45 %** de paragraphes à 1 phrase pour limiter l'édition humaine.

Autres patterns d'édition :
- **Longueur** : claude-cowork 2206 → 1564 mots (-29 %) et deployer-agent-seo 2332 → 2043 (-12 %). L'édition humaine **coupe** systématiquement.
- **Meta** : souvent allongée (claude-cowork 127 → 166 chars), signe d'un travail de réécriture cliquable.
- **H2** : nombre stable ou légèrement diminué (suppression de sections faibles).

## Contraste référence vs drift

Écart le plus net :

| Métrique | Référence | Drift | Ratio |
|---|---|---|---|
| Cadratins / 1000 mots (médiane) | 0.7 | 17.8 | 25x |
| Hook length (médiane) | 5.5 mots | 15 mots | 2.7x |
| % single-sentence paragraphs (médiane) | 49.9 % | 31.4 % | Référence 1.6x plus fragmentée |

Un article qui coche "cadratins bas + hook court + ~50 % paragraphes fragmentés" passe la barre {{COMPANY}}. Un article qui rate ces 3 critères = risque de drift.

## Limites à noter

- **Corpus de 6 articles = petit échantillon.** Les seuils sont à raffiner au fur et à mesure que le corpus grandit.
- **Cadratins dans les H2 "## Étape N —"** : le check actuel compte tout, y compris les H2. Un article comme `automatiser-veille-marketing-ia` (26 cadratins, référence qualité) est flaggué à tort. Fix futur : exclure les H2 du comptage.
- **Hook detection** : actuel regex `\d{2,}` n'attrape pas les hook à 1 chiffre ("8 heures."). Fix futur : regex `\d+`.
- **Anaphora detection** : détection sur premier mot de paragraphe uniquement. Rate les anaphores intra-paragraphes.

## Recommandations de mise à jour des scripts

À valider par user, pas appliqué automatiquement :

### 1. `check_meta.py` — relâcher la plage

Passer de cible stricte 150-160 à tolérance 140-170 (p20-p80 réel du corpus). Déclasser en warning si hors 148-162 (médiane ±10).

### 2. `check_voice.py` — normaliser cadratins par 1000 mots

Remplacer "max 1 cadratin" par "max 5 cadratins / 1000 mots hors H2". Plus réaliste, tolère les H2 style "## Étape N —".

### 3. Nouveau `check_rhythm.py` (6e script)

Critères :
- **pct_single_sentence_paragraphs ≥ 30 %** (warning)
- **pct_single_sentence_paragraphs ≥ 45 %** (cible, tient même après édition)
- **avg_paragraph_words ≤ 32**

### 4. Nouveau `check_hook.py` (7e script)

Critères :
- **hook_first_sentence_words ≤ 12**
- **first_non_rounded_number_position ≤ 3** (1er chiffre précis dans les 3 premières phrases)

### 5. Amélioration `check_links.py`

Le corpus référence montre **médiane 10 liens externes**. Pas de max strict nécessaire, mais au moins 3 liens externes (sourçage) est un signal de crédibilité éditoriale.

## Consommation par le skill

Le skill `seo-writer` peut lire `corpus-baseline.json` pour :
- Calibrer les attentes de longueur (ne pas faire plus court que p20)
- Viser les seuils de rythme (≥ 45 % single-sentence paragraphs)
- Vérifier la densité de chiffres précis (≥ 15 %)

## Mise à jour

Relancer `python3 skills/seo-writer/scripts/analyze_corpus.py content/blog/*.md --output skills/seo-writer/references/corpus-baseline.md --json skills/seo-writer/references/corpus-baseline.json --name "Référence"` dès qu'un nouvel article édité rentre dans le corpus.
