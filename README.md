# Dossier QNX — Global Hackathon 2026

Dossier de recherche et de conception pour le [QNX Global Hackathon](https://qnx.devpost.com/) :
inventaire documenté de ce que QNX SDP 8.0 fournit déjà et de ses manques, classement noté de
140 idées, et quatre cahiers des charges complets.

**Ce dépôt n'est pas une soumission au concours.** C'est le travail amont qui a servi à choisir
un sujet. Il est publié parce que l'inventaire des manques documentés a coûté cher à établir.

## Site

Le site est publié par GitHub Pages à partir des sources Markdown de `src/` (aucune page HTML
committée, donc aucune dérive possible).

Pour le régénérer localement :

```
pip install markdown
python3 tools/build_site.py site/
```

## Contenu

- `src/qnx-inventaire-officiel.md` — ce que QNX fournit déjà, et ~74 trous documentés avec leur page source.
- `src/qnx-classement-final.md` — 169 idées nommées, 140 notées, 29 éliminées avec motif.
- `src/qnx-100-idees-5sem.md` — 100 idées détaillées, chacune rattachée à un trou.
- `src/TAMIS-cahier-des-charges.md` — analyse statique des politiques de sécurité `secpol`.
- `src/GLANE-cahier-des-charges.md` — couche capteurs et publication de périphériques.
- `src/ECLAT-cahier-des-charges.md` — portage WAMR et courtier de capacités.
- `src/VEILLE-cahier-des-charges.md` — moniteur patient à latence d'alarme bornée et prouvée (4e projet, Robotics & Medical ; le code vit dans le dépôt [veille](https://github.com/BaptisteFaisy/veille)).
- `src/veille-codelab/` — codelab en 5 parties : prouver la latence d'une alarme médicale sur QNX 8.0.
- `tools/build_site.py` — générateur du site (une seule implémentation, utilisée en local et en CI).
- `tools/style.css` — feuille de style unique du site.
- `docs/features.html` — page générée : les 91 exigences des quatre cahiers, filtrables par projet et par niveau.

## Avertissement

Les affirmations sur QNX SDP 8.0 datent de novembre 2026 et portent sur la documentation
publique de la version 8.0. Quinze livres de documentation n'ont pas été lus : l'inventaire
n'est pas exhaustif. Trois affirmations ont été corrigées en cours de route et les corrections
sont consignées dans l'inventaire.

## Licence

MIT — voir [LICENSE](LICENSE).
