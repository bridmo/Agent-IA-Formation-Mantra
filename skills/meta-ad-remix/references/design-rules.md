# Règles design — créas Meta {{COMPANY}} (figées)

Système de composition pour les créas « message » (social-native, fond sombre). Source d'exécution : `channels/social/creatives/engine/generate.py` (HTML → PNG via Chrome headless). **Toute créa doit respecter ces règles ; toujours vérifier à l'overlay.**

## 1. Formats & marges
- **9:16** = 1080 × 1920 (stories / reels).
- **4:5** = 1080 × 1350 (feed).
- Marges (padding) : **84 px** haut / gauche / droite.

## 2. Zone morte (selon le format)
- **9:16 (stories)** : les **20 % du bas** sont masqués par l'UI Meta → rien d'important dedans.
- **4:5 (feed)** : l'image entière est affichée → marge basse réduite (~6 %).

## 3. Nombre d'or (φ ≈ 1,618) — un SYSTÈME de proportions, pas deux lignes
Tout dérive de φ, à chaque échelle (comme les cercles Fibonacci de l'Apple : 1·2·3·5·8·13, chacun ×φ).
- **Tailles** = échelle modulaire ×φ (cf. §6).
- **Espacements** = Fibonacci (cf. §7).
- **Hiérarchie = la spirale** : l'œil entre par le grand (focal) et descend vers le petit (preuve). Du grand au petit.
- **Lignes de force 38,2 % / 61,8 %** = des **repères, pas des rails**. On y pose un point d'intérêt quand ça sert la lecture ; on ne déplace jamais un élément hors de sa place fonctionnelle pour y coller.
- **Distribuer, ne pas pinner** : ne jamais coller un seul élément sur une ligne et laisser le reste vide → répartir l'espace libre selon φ pour que la compo soit **pleine et équilibrée, sans trou**.
- **Composition = réponse aux ÉLÉMENTS, pas position figée.** On ne fixe pas un élément toujours au même endroit ; on regarde *ce qu'on veut montrer* et on **répartit l'espace par proportions**. Ex. 3 infos → la 1ʳᵉ prend ~50 % de la place restante, la 2ᵉ ~20 %, la 3ᵉ ~30 % (ordre d'importance). Si on décide qu'un élément secondaire doit être **mis en avant** (ex. les outils), on l'agrandit (~10-15 % H max) et on le place **prominent sous le hook** — pas relégué en socle. La preuve/financement va alors **en bas, séparée**, pour ne pas créer de faux lien (cf. §4). *(impl. : bloc `mid` à 3 étages dans `generate.py`.)*

## 4. Le cadre — zones & alignement (occuper le dessin)
On découpe la créa en zones et on RÉPARTIT ; jamais un élément coincé dans un coin.
| Zone | Élément | Placement |
|---|---|---|
| **Marque** | Votre logo (gauche) + votre preuve sociale (droite) | **haut**, baissés & agrandis (décoincés des coins) — **centres optiques alignés au pixel** (g/d sur la même ligne) |
| **Focal** | Hook (chiffre / tagline) + punchline surlignée | **à GAUCHE**, dans/sur la bande d'or |
| **Preuve (socle)** | Bandeau officiel vos labels officiels | **CENTRÉ, en BAS** |

Contraste d'alignement (cadrage centré haut/bas, contenu à gauche) = **voulu**, pas un mélange accidentel.

**Cohérence sémantique — la PROXIMITÉ crée un lien.** Deux éléments collés sont lus comme liés. Ne jamais poser une info à côté d'un élément auquel elle ne se rapporte pas (exemple vécu : une mention de financement posée sous des logos d'outils se lit « les outils sont financés », ce qui est faux). **Rattacher chaque info à ce dont elle parle** : l'information de financement se colle à l'offre, sous l'accroche, pas aux logos d'outils. À vérifier dans l'éval de CHAQUE créa : *est-ce que chaque élément est à sa place de sens ?*

## 5. Positionnement vertical — focal & socle
- **Focal (9:16)** : centre optique **sur la ligne d'or haute 38,2 %**.
- **Focal (4:5)** : l'espace libre se répartit **φ : 1** (1,618 au-dessus / 1 en dessous) → le focal **remplit le rectangle d'or 38,2 %–61,8 %**, l'air est réparti (pas de trou). *(2 spacers flex-grow 1,618 / 1.)*
- **Nudges par créa (`dy`) = 9:16 SEULEMENT.** On règle le 9:16 à la main (monter/descendre pour l'équilibre global). Le **4:5 garde sa distribution φ:1** : ne JAMAIS lui appliquer le `dy` du 9:16, sinon on casse son équilibre (vide en haut). Chaque format a son propre équilibre.
- **Socle (bandeau)** : un élément de fondation va **EN BAS**. 9:16 → bord bas sur la zone morte (80 %), top à **66,7 %**. 4:5 → descend au vrai bas (bas ~94 %).
- **Toujours vérifier à l'overlay** : tracer 38,2 % / 61,8 %, mesurer le centre du focal et les bornes du bandeau.

## 6. Échelle typographique — modulaire ×φ (px @ 1080 de large)
Niveaux ≈ ×1,618 : **30 · 48 · 62 · 78 · 100 · 126 · 320**.
| Rôle | Taille | Notes |
|---|---|---|
| Chiffre stat géant (`.bignum`) | **320** | focal "stat" (« 42% ») |
| Hook court (`.h1`) | **126** | « Devenez / IA Marketer » |
| Hook medium (`.h1`) | **100** | « 2 500 marketers… » |
| Hook long (`.h1`) | **66–78** | hooks 2-3 lignes (agents) |
| Corps sous un stat (`.body`) | **62** | 700, sous le chiffre |
| Punchline (`.accent`+`mark`) | = niveau du hook | |
| Trustpilot wordmark (Heebo) | 28 | + étoiles 30 |
| Votre logo | 52 | version blanche |

**Le texte garde sa pleine taille sur les DEUX formats** (le réduire vide la compo). Seul le bandeau se met à l'échelle (§8).

## 7. Espacements = Fibonacci
13 · 21 · 34 · 55 · 89. (chiffre→corps = 21 ; énoncé→punchline = 55.)

## 8. Méthode bandeau (golden, chiffré) — référence pour dimensionner un élément
Module = largeur du cadre **W = 1080**. Le bandeau se met à l'échelle `s = H/1920` → **13,2 % de la hauteur dans les DEUX formats**.
- **Largeur** = W/φ = **667 px** (×s) → centré, marges 206 px. Jamais pleine largeur.
- **Ratio** = rectangle **φ² : 1** (2,618) → hauteur = 667/φ² = **255 px** (×s).
- **Logos de réassurance** proportionnés selon le nombre d'or : le carré à 187, le rectangulaire à 187/φ = 116, padding 34. *(×s)*
- Vérifié : 9:16 = 666×254 (top 66,7 %) ; 4:5 = 467×178 (bas ~94 %). Même ratio φ².

## 9. 4:5 = RÉPLIQUE, pas copie
Ne jamais poser les px du 9:16 tels quels. Sur le 4:5 : (1) le **bandeau** se met à l'échelle `s` (reste 13,2 % de H) ; (2) le **texte** reste pleine taille ; (3) le **focal** est distribué φ:1 ; (4) la **zone morte** est réduite (~6 %) et le bandeau descend au vrai bas.

## 10. Surlignage (marqueur) & espacement = règle de SENS
- **Deux phrases** (« 42 %… l'IA. » / « Qu'attendez-vous ? ») → **espace** entre les deux (on peut lire la 1ʳᵉ seule). `mhook` / `mhook_num`.
- **Une seule phrase** (« Devenez IA Marketer en 6 semaines ») → surlignage **INLINE**, interligne normal, **aucun saut de paragraphe**. `mhook_one`.
- L'espace = une **frontière de sens**, pas une déco.

## 11. Couleurs
- **Fond** : dégradé bleu nuit `{{NAVY}} → {{NAVY_2}} → {{NAVY_3}}` (155°) + halo mustard `{{ACCENT}}` (~16 %) haut-droit + halo bleu `{{BLEU}}` (~28 %) bas-gauche. Jamais d'aplat.
- **Accent / surligneur** : mustard `{{ACCENT}}` (texte foncé `{{NAVY}}` dessus).
- **Trustpilot** : vert `#00B67A`. **Tuiles de confiance** : blanc.

## 12. Police
- **Votre police de marque** partout (400 à 700), accroches en 700. Déclarée dans `brain/design-system.md`.
- **Heebo** uniquement pour le bloc Trustpilot (police officielle Trustpilot).

## 13. Composants & logos
- **Surligneur** : `assets/hl.svg` (trait mustard dessiné), `box-decoration-break: clone` pour le multi-lignes.
- **Logos outils / marques = TOUJOURS le vrai asset officiel**, jamais une création/copie/redessin. Si l'asset manque → le récupérer, pas l'inventer.
- **Trustpilot** : logo officiel `assets/tools/trustpilot-white.svg` + étoiles `tp-stars-4.5.svg` + le nombre de clients, pas le nombre d'avis.
- **Bandeau de confiance** : vos labels officiels, logos officiels **tels quels** (interdits : détourer, recolorer, contour, fond similaire → votre mémoire de conformité des logos).
- **Pas d'étiquettes sur les créations centrées message** : le bandeau de preuve suffit. *(Constituez un pool d'étiquettes courtes à partir de `brain/offre.md` pour les autres formats : format, durée, garantie, accompagnement.)*

## 15. Créas à FOND PHOTO (sujet important) — chorégraphie premier plan ↔ arrière-plan
Quand le fond est une **photo** (ex. femme ~40 ans, persona ICP) et non le dégradé bleu nuit :
- **Le système doré reste IDENTIQUE** : focal gauche sur 38,2 % (9:16) / φ:1 (4:5), socle bas, top-bar aligné, bandeau §8. **Seul le fond change.** Ne JAMAIS inventer un layout « spécial photo » (pas de bottom-anchor, pas de taille hors échelle).
- **Scrim 2 couches** (impl. `bg`/`photo` dans `generate.py`) : (vertical) assombrit le top (top-bar) + le bas (socle) ; (horizontal) assombrit la **zone focale GAUCHE** → texte blanc lisible. + `text-shadow` sur `.h1`. Syntaxe : `bg="fichier@position"` (ex. `@72% center` pousse le sujet à droite).
- **RÈGLE DE NON-RECOUVREMENT (le texte ne cache jamais un sujet important).** Un *décor* → on peut recouvrir. Une *personne* (sujet) → jamais. Le focal occupe la **GAUCHE** → le sujet doit occuper la **DROITE** (zone complémentaire). Si l'image met le sujet au centre/à gauche, **deux leviers** : (a) **bouger le fond** — `background-position` ou **régénérer** l'image avec le sujet cadré à droite + deux tiers gauche en négatif sombre propre ; (b) **bouger le premier plan** — déplacer le bloc texte. À vérifier à l'éval : *le texte recouvre-t-il le visage / le sujet ?* Si oui → corriger avant de valider.
- **Brief image = composer POUR la grille** : sujet à droite, négatif sombre à gauche pour le focal, légèrement sombre pour que le blanc tienne.

## 14. Vérification (obligatoire) — revue de cohérence globale AU PIXEL
Deux temps, toujours :
1. **À la création** : poser chaque élément selon §1-13 (proportions φ, zones, sens).
2. **À l'évaluation** : avant de valider, une **revue de cohérence globale au moindre pixel**. Si ce n'est pas pixel-perfect, ça **casse toute l'idée du graphisme** → ne pas valider.

**Mesurer (script overlay/PIL), jamais « à l'œil » seul :**
- **Alignements** : logo ↔ bloc de preuve = même centre optique (écart cible **0 px**, toléré ≤ 3 px sur 1920). Mesurer les centres réels, pas se fier au box CSS (les SVG ont des offsets internes → nudge px si besoin).
- **Focal** : centre sur la ligne d'or (9:16) / rectangle φ:1 (4:5).
- **Bandeau** : largeur, ratio φ², % (top/bas), centrage.
- **Zone morte** : rien d'important sous 80 % (9:16). Si le socle (tags/bandeau) doit laisser la zone morte libre, **la compter dans la proportion** et le remonter (ex. tags à ~76 %, pas collés à 80 %).
- **Absence de trou** ; **cohérence de sens** (§4 : chaque info à sa place).
- **Les 8 créas entre elles** : même top-bar, même socle, même grille → cohérence de série.
