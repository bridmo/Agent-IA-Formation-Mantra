# Meta Ad Library — URLs de veille par concurrent

Source de la liste : `brain/competitors.md`. Annonces **actives**, pays **FR**.

La recherche par mot-clé remonte parfois des homonymes : toujours vérifier la page annonceur
(nom exact + logo) avant de collecter. Une fois la page officielle identifiée, préférer l'URL
filtrée par page (`view_all_page_id=<ID>`) et la noter ici pour les runs suivants.

| Concurrent | URL de recherche | Page ID (à remplir au 1er run) |
|---|---|---|
| LiveMentor ⭐ | https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=FR&q=LiveMentor&search_type=keyword_unordered&media_type=all | |
| Databird ⭐ | https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=FR&q=Databird&search_type=keyword_unordered&media_type=all | |
| École Cube ⭐ | https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=FR&is_targeted_country=false&media_type=all&search_type=page&sort_data[direction]=desc&sort_data[mode]=total_impressions&view_all_page_id=570003109538598 | **570003109538598** (page officielle, triée impressions desc) |
| Marjolaine Grondin / bootcamp IA ⭐ | https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=FR&q=Marjolaine%20Grondin&search_type=keyword_unordered&media_type=all | |
| Ades Bootcamp ⭐ | https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=FR&q=Ades%20Bootcamp&search_type=keyword_unordered&media_type=all | |
| Joinlion (Lion) | https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=FR&q=Joinlion&search_type=keyword_unordered&media_type=all | |
| Scalezia | https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=FR&q=Scalezia&search_type=keyword_unordered&media_type=all | |
| OpenClassrooms | https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=FR&q=OpenClassrooms&search_type=keyword_unordered&media_type=all | |
| Growth Tribe | https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=FR&q=Growth%20Tribe&search_type=keyword_unordered&media_type=all | |
| Le Wagon | https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=FR&q=Le%20Wagon&search_type=keyword_unordered&media_type=all | |
| Ironhack | https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=FR&q=Ironhack&search_type=keyword_unordered&media_type=all | |

## Données à collecter par annonce

- ID de l'annonce (Library ID) si visible
- Date de début de diffusion (« Diffusion depuis le … ») → **longévité = proxy performance**
- Nombre de variantes (« X annonces utilisent ce contenu ») → scaling = signal fort
- Format : image / vidéo / carrousel
- Texte primaire (complet), titre, description, CTA
- Screenshot du rendu

## Hors Meta (référence)

Joinlion et Databird sont aussi actifs sur LinkedIn Ads (Ad Library LinkedIn :
https://www.linkedin.com/ad-library/search?companyIds=) — hors scope v1, à brancher si besoin.
