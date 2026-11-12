# Dossier QNX — Global Hackathon 2026

Travail de recherche et de conception mené en novembre 2026 pour le
[QNX Global Hackathon](https://qnx.devpost.com/) (dépôt des soumissions le 15 décembre 2026).

Ce dépôt ne contient **pas** un projet soumis au concours : c'est le dossier de travail qui a
servi à choisir un sujet. Il est publié parce que l'inventaire qu'il contient a coûté cher à
établir et peut servir à d'autres.

## Ce qu'on y trouve

| Document | Contenu |
|---|---|
| [Fonctionnalités](features.html) | Les **91 exigences** des quatre cahiers, extraites automatiquement de leurs tableaux, filtrables par projet et par niveau S/C/X. |
| [Inventaire officiel](inventaire.html) | Ce que QNX SDP 8.0 **fournit déjà** (IDE Momentics, SAT, chaîne `secpol`, HAM, QPLMS, QFS, hyperviseur et ses 20 vdev, io-sock, conteneurs, ports open source) et les **~74 trous documentés**, chacun avec la page de documentation source. |
| [Classement](classement.html) | 169 idées nommées, 140 notées sur une grille explicite, 29 éliminées avec motif. |
| [100 idées détaillées](idees.html) | Les 100 idées retenues à l'étape précédente, chacune rattachée au trou qu'elle exploite. |
| [Tamis](tamis.html) | Cahier des charges complet — analyse statique et preuve des politiques de sécurité `secpol`. |
| [Glane](glane.html) | Cahier des charges complet — couche capteurs et publication de périphériques. |
| [Éclat](eclat.html) | Cahier des charges complet — portage de WAMR (WebAssembly) et courtier de capacités. |
| [Veille](veille.html) | Cahier des charges complet — moniteur patient à latence d'alarme bornée et prouvée. |
| [Codelab Veille](codelab-veille.html) | Codelab en 5 parties — prouver la latence d'une alarme médicale sur QNX 8.0. |

## Les quatre sujets poussés jusqu'au cahier des charges

**Tamis** — *Developer Tooling & Host Tools*. La documentation QNX reconnaît que la revue des
règles inutiles est manuelle, que la politique générée n'est pas utilisable telle quelle, et
qu'il n'existe **aucune analyse statique avant déploiement**. Tamis analyse une politique
`secpol` à froid : chemins transitifs de privilège avec contre-exemple, preuve d'absence de
chemin, minimisation avec preuve d'équivalence, diff sémantique, lint de typage. Point décisif :
`secpolcompile` est un **utilitaire hôte**, donc le test différentiel contre le compilateur
officiel ne nécessite aucune cible.

**Glane** — *Low-level Software*. QNX livre un framework de publication de périphériques et
**un seul** publisher (`usblauncher_otg`, orienté USB/stockage/média). Aucune API pour en écrire
un, aucune simulation sans matériel, aucun validateur de schéma, aucune mesure de latence, et
aucune abstraction capteur au-dessus des frameworks GPIO et SPI pourtant documentés.

**Éclat** — *Open-Source Contribution & Ports*. Aucun runtime WebAssembly n'est porté sur QNX
(absence vérifiée dans l'index officiel des ports). WAMR porté, plus un courtier de capacités :
chaque import du module devient un message vers un gestionnaire de ressources qui décide selon
une politique dont le défaut est de **tout refuser**. Trois couches d'isolation indépendantes :
le bac à sable WebAssembly, le processus sans abilities, la politique appliquée par le noyau.

**Veille** — *Robotics & Medical*. QNX ne fournit aucun framework d'alarme médicale
IEC 60601-1-8, et le System Profiler mesure des échantillons ponctuels sans jamais prouver
de borne pire-cas. Veille est un moniteur patient dont la chaîne capteur→alarme a une latence
bornée et **prouvée** par exploration exhaustive des 4800 états de défaillance atteignables
(5×3×2×5×32), avec double preuve (modèle C11 pur + jumeau Python, puis kernel trace sur
cible) et rapport d'audit empreinté SHA-256 exploitable en IEC 62304. Le projet vit dans
[son propre dépôt](https://github.com/BaptisteFaisy/veille) ; le codelab qui l'accompagne
est publié ici.

## Méthode, et ses limites

Le classement est né d'un constat : le facteur limitant n'est pas le nombre d'idées mais le
nombre de **manques documentés**. Une boîte combinatoire de 10 000 cellules ne produit que
392 idées distinctes (facteur de duplication mesuré : 25). Le travail utile a donc été de lire
la documentation — y compris les livres que personne ne lit, comme le guide de l'IDE, qui a
invalidé rétroactivement cinq « trous » supposés.

Limites assumées :

- **15 livres de documentation restent non lus** (SMMUMAN, PCI Server, Device Publishers en
  partie, Discontinuation Notice, Boot Optimization, Building Embedded Systems, QNX Software in
  the Cloud, Technotes, etc.). L'inventaire n'est pas exhaustif.
- Les notes d'originalité et de qualité de démonstration sont des **estimations**, pas des
  mesures.
- Trois affirmations ont été **corrigées en cours de route** : `inotify` existe bien en QNX 8.0
  (dans `libfsnotify.so`) ; l'IDE Momentics fournit déjà un profileur, l'analyse mémoire, le
  debug d'interblocage et l'analyse des temps de démarrage ; QFS fournit déjà un système de
  fichiers à protection d'intégrité. Les idées fondées sur ces affirmations ont été écartées.
- Aucun des trois sujets n'a encore été exécuté sur QNX : la licence QNX Everywhere n'était pas
  installée au moment de la rédaction. Les cahiers distinguent donc ce qui est démontrable sur
  un poste Linux de ce qui exige la cible.

## Régénérer le site

```
pip install markdown
python3 tools/build_site.py site/
```

Le site est construit par la CI à partir des sources Markdown de `src/` : aucune page HTML
n'est committée, il n'y a donc pas de dérive possible entre le texte et le site.
