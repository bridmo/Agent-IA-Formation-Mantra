# .claude/

Configuration de Claude Code pour ce repo.

| Fichier | Rôle |
|---|---|
| `skills/` | Liens symboliques vers les skills à rendre découvrables |
| `settings.local.example.json` | Modèle de réglages locaux : copiez-le en `settings.local.json` |
| `launch.json` | Serveurs de preview (aperçu de vos pages dans le navigateur intégré) |

## Les liens symboliques de skills

Claude Code découvre les skills présents dans `.claude/skills/`. Pour éviter de dupliquer les fichiers, on y met des liens :

```bash
ln -s ../../skills/page-cro .claude/skills/page-cro
```

**N'activez que ce que vous utilisez.** Soixante-huit skills tous actifs, c'est soixante-huit descriptions à évaluer à chaque tour : ça ralentit et ça brouille le déclenchement. Commencez par trois ou quatre.

Pour activer d'un coup ceux dont vous avez besoin :

```bash
for s in page-cro copywriting seo-strategy paid-ads; do
  ln -s "../../skills/$s" ".claude/skills/$s"
done
```
