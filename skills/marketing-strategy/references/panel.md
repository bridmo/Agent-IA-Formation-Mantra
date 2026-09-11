# Le panel de challenge : 5 rôles de direction

On n'improvise pas une contradiction. Chaque plan passe devant cinq rôles ; chacun a une seule question et un angle d'attaque. On garde ce qui résiste aux cinq. Inspiré du mécanisme `expert-panel` (scoring multi-rôles), mais calibré pour votre contexte et orienté décision, pas notation.

| Rôle | La question qu'il pose | Ce qu'il attaque | Data qu'il exige |
|---|---|---|---|
| **CEO allocateur de capital** | Est-ce le meilleur emploi de nos ressources rares (temps équipe, budget, attention) ? | Le coût d'opportunité : ce qu'on ne fait pas en faisant ça. Un plan qui disperse une petite équipe sur trop de fronts. | Charge par personne, budget par euro de CA visé |
| **CMO** | Le mix de canaux et le positionnement tiennent-ils ? | La dépendance à un canal, un positionnement flou, un objectif de volume qui se remplit par le canal le moins rentable. | CA par SQL par canal, mix de financement, part du financement public |
| **Directeur growth** | Comment on le lit, et quand on décide ? | L'absence de métrique de succès, de gate datée, de contre-mesure. Un test sans critère d'arrêt. | Baseline et seuil de décision par action |
| **DAF / marge** | Ça crée de la marge ou du chiffre à perte ? | Un ratio CA/spend sous le seuil de marge. Un budget qui dépense avant d'encaisser sans condition. | Marge brute par vente, ratio par canal |
| **Expert du secteur** | La réglementation et le marché le permettent-ils ? | Un levier interdit (remise sur un dispositif financé), une éligibilité qui expire (RS), une demande qui n'existe pas (données publiques du marché). | Plafonds par voie, dates de certif, achats réellement financés |

## Méthode

1. Faire tourner les cinq sur chaque prémisse et chaque axe du plan.
2. Une objection ne compte que si elle s'appuie sur une donnée ou une logique, jamais sur un principe.
3. Ce qui tombe devant un rôle est signalé, pas supprimé : {{OWNER}} arbitre.
4. Conclusion : les prémisses qui résistent, celles qui tombent, et le vrai problème en une phrase.

## Le piège du consensus

Le panel ne sert à rien s'il valide tout. Si aucune prémisse ne tombe, le challenge a été mou : reprendre chaque affirmation et chercher activement la donnée qui la contredirait. Un bon challenge fait tomber au moins une prémisse ou nomme un angle mort que le plan n'adresse pas.

## Où trouver les chiffres que le panel exige

Ne pas figer de valeurs ici, elles périment. Sources courantes : économie par canal et réachat dans la mémoire `project_economie_canaux`, saisonnalité dans `feedback_saisonnalite_automne`, plafonds et voies dans `brain/contraintes-marche.md`, marché du financement public dans `project_donnees_marche`. Tout le reste se pull en live (voir la section Latent vs déterministe du SKILL).
