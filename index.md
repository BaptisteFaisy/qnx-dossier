# Dossier QNX — Global Hackathon 2026

Travail de recherche et de conception mené en novembre 2026 pour le
[QNX Global Hackathon](https://qnx.devpost.com/) (dépôt des soumissions le 15 décembre 2026).

Ce dépôt ne contient **pas** un projet soumis au concours : c'est le dossier de travail qui a
servi à choisir un sujet. Il est publié parce que l'inventaire qu'il contient a coûté cher à
établir et peut servir à d'autres.

## Ce qu'on y trouve

| Document | Contenu |
|---|---|
| [Fonctionnalités](features.html) | Les **116 exigences** des cinq cahiers, extraites automatiquement de leurs tableaux, filtrables par projet et par niveau S/C/X. |
| [Inventaire officiel](inventaire.html) | Ce que QNX SDP 8.0 **fournit déjà** (IDE Momentics, SAT, chaîne `secpol`, HAM, QPLMS, QFS, hyperviseur et ses 20 vdev, io-sock, conteneurs, ports open source) et les **~74 trous documentés**, chacun avec la page de documentation source. |
| [Classement](classement.html) | 169 idées nommées, 140 notées sur une grille explicite, 29 éliminées avec motif. |
| [100 idées détaillées](idees.html) | Les 100 idées retenues à l'étape précédente, chacune rattachée au trou qu'elle exploite. |
| [Tamis](tamis.html) | Cahier des charges complet — analyse statique et preuve des politiques de sécurité `secpol`. |
| [Glane](glane.html) | Cahier des charges complet — couche capteurs et publication de périphériques. |
| [Toile](toile.html) | Cahier des charges complet — pilote virtio-gpu 2D pour QNX 8.0. |
| [Toile — en direct](toile-demo.html) | L'invité QNX 8.0 de Toile, affichage virtio-gpu et console série. |
| [Éclat](eclat.html) | Cahier des charges complet — portage de WAMR (WebAssembly) et courtier de capacités. |
| [Veille](veille.html) | Cahier des charges complet — moniteur patient à latence d'alarme bornée et prouvée. |
| [Codelab Veille](codelab-veille.html) | Codelab en 5 parties — prouver la latence d'une alarme médicale sur QNX 8.0. |
| [Réplique — en direct](replique.html) | L'invité QNX 8.0 de la démo Déclic : la trace noyau figée au crash, décodée par l'oracle `traceprinter`. |
| [Tamis — en direct](tamis-demo.html) | Le cœur C de Tamis compilé par `qcc`, tournant dans l'invité QNX 8.0 sur une politique `secpol` réelle. |
| [Glane — en direct](glane-demo.html) | L'invité publie ses capteurs dans `/dev/shmem` et expose `/dev/sensors`, gestionnaire de ressources QNX. |
| [Veille — en direct](veille-demo.html) | Le cœur C de Veille dans QNX : 4 800 états explorés, 600 échantillons rejoués, `/dev/veille` en service. |

## Les cinq sujets poussés jusqu'au cahier des charges

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

**Toile** — *Low-level Software*. Le SDP 8.0 livre une vingtaine de périphériques
virtuels pour son hyperviseur — `virtio-blk`, `virtio-net`, `virtio-snd` — mais
**aucun pour le GPU** : dans une machine virtuelle QNX, l'écran est inutilisable
sans passe-plat, et le SDP ne livre pas de pilote d'écran tiers exploitable hors
« Screen Board Support packages ». Toile écrit le **pilote virtio-gpu 2D** qui
manque — énumération PCI, transport virtio, controlq, scanout, framebuffer, `flush` —
et le publie comme gestionnaire de ressources `/dev/gpu0`. Le cœur (machine à
commandes, invariants, verdicts) est portable et testé sur PC, avec jumeau Python et
différentiel ; la cible apporte la preuve que ce cœur pilote un vrai périphérique.
L'essai E4 — accès au DDK hyperviseur sous licence non commerciale — a été **tranché
négativement** : le volet hôte est abandonné, le projet reste faisable en invité QEMU.
Le dépôt est public et la [vitrine en direct](toile-demo.html) montre l'invité QNX 8.0
affichant la mire peinte par un client dans le framebuffer virtio-gpu.

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
[son propre dépôt](https://github.com/BaptisteFaisy/veille) et se visite en ligne sur
[son site](https://baptistefaisy.github.io/veille/) — chiffres calculés depuis le code,
preuves réellement rejouées au build ; le codelab qui l'accompagne est publié ici.

## Les vitrines en direct

Quatre des cinq sujets — Tamis, Glane, Toile, Veille — et Réplique ne sont pas seulement des
documents : **leur code tourne dans de vrais invités QNX 8.0** (SDP 8.0 installé, QEMU sur le
r630), et les cinq invites sont ouvertes au public. Éclat n'a pas d'invité : son runtime WAMR
compile et se lie bien pour QNX (`qcc`, `nto x86_64` et `nto aarch64le`), mais la démo
reste sur l'hôte Linux.

| Sujet | Invité en direct | Ce que la page montre |
|---|---|---|
| [Réplique](replique.html) | [r630:8091](https://r630-debian.tail3a8bdf.ts.net:8091/) | L'invité QNX 8.0 de la démo Déclic ; la trace noyau décodée par l'oracle officiel `traceprinter`. |
| [Tamis](tamis-demo.html) | [r630:8092](https://r630-debian.tail3a8bdf.ts.net:8092/) | Le cœur C, compilé par `qcc`, rend ses verdicts **dans QNX** : `TAMIS_PATH_FOUND`, correctif minimal, trou de lint. |
| [Glane](glane-demo.html) | [r630:8091/glane](https://r630-debian.tail3a8bdf.ts.net:8091/glane) | `glaned` publie les capteurs dans `/dev/shmem` et `/dev/sensors`, en boucle, dans l'invité. |
| [Toile](toile-demo.html) | [r630:8091/toile](https://r630-debian.tail3a8bdf.ts.net:8091/toile) | Le pilote `toile-gpu` scanoute en 1280×800 et présente des images à 30 im/s (`present_ko=0`). |
| [Veille](veille-demo.html) | [r630:8091/veille](https://r630-debian.tail3a8bdf.ts.net:8091/veille) | 4 800 états explorés, 600 échantillons rejoués, `/dev/veille` en service (SCHED_FIFO 62), alarme à la déconnexion. |

L'écran de gauche est la console VGA de l'invité — les boutons injectent des touches ; la
console de droite est le port série. **Chaque invite s'arrête après 5 minutes sans visite**
et se relance tout seul à la visite suivante : un écran « INVITÉ ARRÊTÉ » ou
« INVITÉ EN DÉMARRAGE » est normal, la cible démarre en une quarantaine de secondes.

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
- Cette limite a été levée depuis la rédaction : **les cinq sujets s'exécutent sur de vrais
  invités QNX 8.0** (SDP 8.0 installé, QEMU sur le r630) et leurs vitrines sont ouvertes au
  public — voir « Les vitrines en direct » plus haut. Ce qui n'est pas démontré reste écrit
  noir sur blanc dans chaque vitrine (ce qui tourne, ce qui n'est pas démontré, ce qui n'est
  pas mesuré).

## Régénérer le site

```
pip install 'markdown==3.5.2'
python3 tools/build_site.py site/
```

Le site est construit par la CI à partir des sources Markdown de `src/` : aucune page HTML
n'est committée, il n'y a donc pas de dérive possible entre le texte et le site.
