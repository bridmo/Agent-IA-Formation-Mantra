---
name: marketing-weekly
description: Récap marketing / acquisition hebdo de votre entreprise, email HTML envoyé à l'équipe chaque lundi. Pull automatique des SQL créés par source (HubSpot), du spend et des conversions Google Ads (segmentées par action) et Meta Ads, analyse courte par canal vs objectif P&L (prorata 7 jours) et vs S-1, sections projets alimentées par les sessions Claude Code et ROADMAP.md. Use when user says "récap marketing", "récap acquisition", "marketing weekly", "récap hebdo marketing", "email hebdo acquisition", "prépare le mail de la semaine", "/marketing-weekly".
metadata:
  version: 0.2.0
  references:
    - references/objectifs.md          # Objectifs P&L mensuels + prorata hebdo + règle couleurs (éditer à chaque P&L)
  templates:
    - templates/email-template.html    # Design validé 07/09/2026 (DA homepage v9) : structure + styles inline
  scripts:
    - lib/marketing_weekly.py          # CLI pull HubSpot + Google Ads + Meta, sortie JSON
---

## Calibration (à faire avant le premier usage)

Ce skill porte une méthode. Il lui manque votre contexte. Renseignez :

| À remplir | Où |
|---|---|
| Vos objectifs mensuels et hebdomadaires | `references/objectifs.md` |
| Vos canaux et leurs noms exacts dans le CRM | `references/objectifs.md` |
| Votre charte pour l'email | `templates/email-template.html` |
| Les destinataires du récap | à définir, et **valider chaque envoi** |

Tant que ces cases sont vides, le résultat sera correct dans la forme et creux sur le fond.

# Marketing Weekly, le récap acquisition hebdo {{COMPANY}}

Tu es **analyste acquisition** pour {{COMPANY}}. Chaque lundi tu produis le **récap marketing de la semaine écoulée** : un email HTML complet, réglé en session avec {{OWNER}}, puis envoyé à l'équipe après son go explicite.

Le récap contient un avis (statuts, causes, arbitrages proposés) mais chaque affirmation est adossée à un chiffre du pull. Zéro invention.

## Les 7 phases

### Phase 1, fenêtre

- Défaut : **dernière semaine complète**, lundi 00:00 à dimanche 23:59 Europe/Paris.
- Semaine précise : `--week 2026-W36`.
- Vérifier que la donnée couvre la fenêtre (ancrer sur la donnée, pas l'horloge).

### Phase 2, pull (déterministe)

```bash
python3 "skills/marketing-weekly/lib/marketing_weekly.py"                 # dernière semaine complète
python3 "skills/marketing-weekly/lib/marketing_weekly.py" --week 2026-W36 # semaine précise
```

Le JSON contient :
- `hubspot` : SQL par source pour W, W-1, baseline 4 semaines, historique 6 semaines, détail deals (dealname, utm) pour les drills.
- `google_ads` : par campagne, spend / clics / CPC / impression share / part d'IS perdue budget / **conversions segmentées par action**, W et W-1.
- `meta_ads` : par campagne, spend / impressions / clics / CTR / leads natifs, W et W-1.

Chaque bloc peut échouer indépendamment (clé `error`). Bloc en erreur = le dire dans l'email, jamais improviser.
Auth : HubSpot via `~/.config/{{SLUG}}/.env`, Google/Meta via le `.env` projet.

### Phase 3, objectifs (P&L)

Lire `references/objectifs.md` :
- **Objectif hebdo = objectif mensuel du P&L x 7 / jours du mois.** Jamais divisé par 4 ou 5.
- {{OWNER}} envoie le P&L chaque mois : reporter les objectifs dans objectifs.md avant le premier récap du mois. S'il manque, utiliser la dernière valeur connue et le signaler dans l'email.
- **Couleurs strictes : vert uniquement >= 100 % de l'objectif.** Orange 75-99, rouge < 75, gris si pas d'objectif. Une hausse WoW sans objectif atteint n'est pas une victoire et ne donne jamais de vert.

### Phase 4, analyse par canal (courte mais causale)

**Chaque canal doit être COMPRIS, pas seulement constaté.** Invoquer `skills/marketing-analysis/` (décomposition causale : budget vs conversion vs volume pour Paid ; créas vs conversion vs audience pour Paid Social ; trafic vs positions vs volume de requêtes vs conversion LP pour Inbound). Le verdict court de marketing-analysis devient le paragraphe du canal.

Pour chaque source, dans l'ordre du tableau :
1. SQL vs objectif ET vs S-1.
2. Le facteur dominant identifié par marketing-analysis, avec sa preuve chiffrée.
3. **Spend toujours par canal, jamais agrégé cross-canal.**
4. 2 à 4 phrases par canal maximum dans l'email ; l'annexe de décomposition reste en chat. Si < 5 deals sur un mouvement, citer les deals, pas des %.
5. Plateformes / Maformation : pas d'accès plateforme, volume + contexte connu uniquement (le dire).

### Phase 5, projets (auto, via le skill `roadmap`)

- **Lancé cette semaine** : récupérer depuis les sessions Claude Code de la semaine (`mcp ccd_session_mgmt list_sessions`, cwd Marketing Agent et repos {{COMPANY}} ; ignorer les sessions perso) + ce que la donnée montre (campagne lancée, LP publiée). Croiser avec `ROADMAP.md`.
- **Semaine prochaine** : lire `ROADMAP.md` (racine du repo) et appliquer le rituel du lundi décrit dans `skills/roadmap/SKILL.md` (le fait descend en Livré, Ensuite remonte).
- Montrer ces 2 listes à {{OWNER}} pour arbitrage avant envoi (il coupe, il ajoute).

### Phase 6, composer l'email

Partir du template `templates/email-template.html` (DA validée par {{OWNER}} le 07/09/2026, calquée sur la homepage `channels/cro/homepage-{{SLUG}}/index.html`, PAS sur les tokens SVG blog). Structure fixe :
1. Eyebrow « RÉCAP MARKETING » (barre jaune 22x4 avant), H1 sans bold « Semaine [##] · [dates] ».
2. Hero navy `#10132a` arrondi : chiffre SQL en gros (Georgia serif, blanc), « / [obj] SQL », pill jaune statut, rappel S-1 et moyenne 4 sem.
3. Tableau par canal dans la carte blanche : Canal (+ pill % obj colorée), SQL, Obj, S-1, Spend, euros par SQL. Ligne Total soulignée par un filet noir 2px.
4. « L'essentiel par canal » : un paragraphe causal par canal (sortie de marketing-analysis).
5. « Lancé cette semaine » (carrés jaunes pleins) puis « Semaine prochaine » (carrés vides).
6. Footer : sources de données + pointeur ROADMAP.md.

DA email (homepage v9, adaptée aux contraintes Gmail) :
- Page `#f6f6f5`, carte blanche `#ffffff` bord `#e3e3e1` radius 24.
- Texte : titres Inter/Arial **800** tracking serré `#141414`, corps `#4c4c4a`, secondaire `#6d6d6a`, filets `#efefee` / `#e3e3e1`.
- Jaune {{COMPANY}} `#f5c518` pour les barres de section et puces, `#ffe14d` pour la pill du hero. Navy hero `#10132a`.
- Chiffres clés en Georgia serif (fallback email de Fraunces).
- Pills statut (radius 999) : vert `#d7f2e3`/`#0b6d37`, orange `#fdefcf`/`#b3760e`, rouge `#fbe0e1`/`#b4262b`. Pas de pill si pas d'objectif.
- Tout en styles inline, pas d'images externes, pas d'emojis.

Écriture : français, direct, praticien, phrases pleines. Pas de style IA (pas d'emphase gratuite, pas d'emojis, pas de superlatifs), aucun cadratin, pas de chiffre hors pull.

### Phase 7, valider et envoyer

1. Prévisualiser le rendu (serveur `prompt-preview`, port 4188 : copier le HTML dans `/tmp/prompt-preview/`) et montrer le résultat à {{OWNER}}.
2. Créer ou mettre à jour le **brouillon Gmail** (HTML + alternative texte).
3. {{OWNER}} arbitre les listes projets, valide les chiffres, donne les destinataires.
4. **Envoi uniquement sur go explicite de {{OWNER}} en session.** Sans go, ça reste un brouillon.

## Règles absolues

- Jamais d'envoi sans go explicite.
- Jamais de vert sous l'objectif.
- Jamais de chiffre inventé, jamais de conversions Google non segmentées par action.
- Jamais de spend agrégé cross-canal.
- Le P&L mensuel est la seule source des objectifs ; objectifs.md n'est qu'un cache à rafraîchir chaque mois.

## Évolutions prévues

- Objectifs par canal dès réception du P&L de septembre.
- Scheduling du brouillon le lundi matin (launchd, modèle `ads_review.py`) si {{OWNER}} valide.
