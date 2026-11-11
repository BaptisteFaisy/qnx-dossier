# Tamis — analyse statique et preuve des politiques de sécurité QNX

**Nom de travail : « Tamis »** (passer la politique au crible avant qu'elle ne passe en production).
Version 0.1 — 11 novembre 2026 — projet candidat au QNX Global Hackathon, catégorie **Developer Tooling & Host Tools**.
Classement interne : 3ᵉ sur 140 idées notées (15/16) **et 1ᵉr dès que la licence QNX est installée** dans une variante de la grille ; seul projet du top 7 démontrable **intégralement sans cible**.
Visé explicitement : bonus **Best use of QNX-specific Technologies** (les politiques de sécurité y sont nommément citées).

> Note de nommage : l'idée a d'abord été appelée « Oracle ». Ce nom est **interdit** — le règlement proscrit les marques de tiers dans les supports de soumission, et la vidéo en fait partie.

---

## 0. Lecture rapide

**Ce que c'est.** Un outil hôte qui lit une politique de sécurité QNX (`secpol`) **avant déploiement** et répond à quatre questions que la chaîne officielle ne pose pas : cette règle est-elle atteignable ? ce type peut-il, par une chaîne d'intermédiaires, atteindre ce type critique ? quelles règles sont mortes ? cette modification élargit-elle un privilège ?

**La promesse, en une phrase.** Une politique de sécurité passe d'un texte que l'on relit à la main à un artefact **analysé, minimisé, diffable et prouvé**, avec un certificat de non-interférence exploitable dans un dossier ISO 26262, IEC 62304, EN 50128 ou UNECE R155.

**Trois idées qui portent le projet.**

1. **Compléter la chaîne officielle, jamais la doubler.** QNX génère (`secpolgenerate`, avec mode diff incrémental), compile (`secpolcompile`), applique (`secpolpush`) et surveille (`secpolmonitor`). La documentation reconnaît elle-même que **tout l'aval est manuel** : revue des règles inutiles, fusion, stabilisation, vérification du typage. Tamis occupe exactement cet espace.
2. **L'analyse statique n'existe pas.** C'est écrit noir sur blanc dans le guide : la politique ne peut pas être validée avant exécution. Tamis est le premier maillon « à froid ».
3. **Le compilateur officiel tourne sur l'hôte.** `secpolcompile` est un utilitaire hôte : on peut donc tester Tamis **par différentiel** contre le vrai compilateur, sans jamais démarrer une cible. C'est ce qui rend le projet vérifiable à 100 % sur un poste de développement.

**Trois niveaux d'ambition.** **S** (socle), **C** (complet), **X** (extrême).

**À valider avant d'écrire la moindre ligne de produit** (section 10) : cinq essais, dont E1 — lire et geler la grammaire exacte du langage de politique — et E2 — confirmer que `secpolcompile` s'exécute sur l'hôte et produit des fichiers d'événements exploitables.

**Statut des affirmations.** Section 14 : la syntaxe exacte du langage n'a **pas** encore été lue page à page. C'est le premier travail, pas une hypothèse de plus.

---

## 1. Contexte et cas d'usage

### 1.1 Qui a ce problème

| Acteur | Besoin | Ce qu'il fait aujourd'hui |
|---|---|---|
| Intégrateur système certifié ISO 26262 / IEC 62304 / EN 50128 | Prouver que la partition non critique ne peut pas atteindre la critique | Relecture humaine, tableaux Excel, argumentaire prose |
| Responsable cybersécurité UNECE R155 | Montrer que les privilèges sont au moindre privilège, et ce qui a changé entre deux versions | Diff文本uel, revue manuelle |
| Développeur QNX | Comprendre pourquoi un accès est refusé en recette, sans relancer 20 fois la génération | Essai-erreur, lecture du fichier d'erreurs |
| Auditeur externe | Vérifier la cohérence du typage de tous les processus, y compris ceux qui ne tournent pas | `pidin -f a_n…` sur un système en marche |
| Équipe produit | Empêcher une régression de privilèges d'entrer dans une version | Rien — aucune revue automatique |

### 1.2 Pourquoi c'est un vrai marché

La politique de sécurité est **l'argument de vente central** de QNX OS for Safety : c'est elle qui rend la non-interférence démontrable. Or la chaîne officielle s'arrête à la génération. Tout ce qui suit — comprendre, réduire, prouver, comparer — est à la charge de l'intégrateur, à la main, sur des politiques de plusieurs centaines de règles.

### 1.3 Ce que Tamis n'est pas

Ni un générateur de politique, ni un moniteur temps réel, ni une matrice attaque/mitigation, ni un analyseur de code source. Ces quatre choses existent déjà ou sortent du périmètre (section 3.2).

---

## 2. Ancrage documentaire

### 2.1 Ce que QNX fournit déjà (à ne pas réinventer)

| Élément | Rôle |
|---|---|
| `secpolgenerate` | Génère une politique en observant le système ; **possède un mode diff incrémental** contre une politique existante |
| `secpolcompile` | Compile la politique texte vers le binaire inséré dans l'IFS — **utilitaire hôte** |
| `secpolpush` | Applique la politique sur le système |
| `secpolmonitor` | Sortie temps réel des événements de politique |
| `libsecpol` | Baisser ses privilèges après initialisation, spawner avec privilèges |
| `libsecpolev` | Consommation des événements de trace de politique |
| `/dev/secpolgenerate/errors`, `/dev/secpolgenerate/unused` | Erreurs rencontrées, règles non utilisées |
| ~70 abilities statiques + abilities dynamiques personnalisées | `abilities.html`, `abilities_reference.html` |
| Pathtrust, fonctions fortifiées, `security_matrix`, `mkqnximage` (mode démo sécurité) | Autres briques de sécurité |
| IDE QNX Momentics | Profileur, analyse mémoire, System Profiler (debug d'interblocage), System Builder — **mais aucun outil de politique** |

### 2.2 Les trous exploités (sourcés, System Security Guide)

| Code | Trou, tel que la doc le formule | Page |
|---|---|---|
| S1 | La revue des règles inutiles est **manuelle** : « QNX recommends that you review the security policy specifically to locate processes with abilities that they don't need » | `review_policies.html` |
| S2 | La politique générée n'est **pas utilisable telle quelle** | `using_secpolgenerate_secure_system.html` |
| S3 | **Aucune analyse statique / pré-exécution** : la politique ne peut pas être validée avant déploiement | `using_security_policies.html` |
| S4 | Des échecs restent **invisibles** à l'outil : « There are ways in which a system can fail that are invisible to secpolgenerate and thus won't show up in its errors file » (permissions de fichiers, root→non-root) | `troubleshooting.html` |
| S6 | **Instabilité entre exécutions** : la politique générée varie d'un run à l'autre | `security_policy_maintenance.html` |
| S7 | `default_spawn_type` **n'est jamais généré**, il faut l'ajouter à la main | `tuning.html` |
| S8 | Analyse d'**élévation de privilèges artisanale** : la doc prescrit l'essai-erreur sur le graphe `settypeid` / `gain_priv` | `secpol_language.html`, `troubleshooting.html` |
| S9 | **Fusion manuelle** des nouvelles règles après un diff incrémental | `security_policy_maintenance.html` |
| S10 | **Vérification du typage complet manuelle** (`pidin -f a_n…`) | `security_policy_maintenance.html` |
| S13 | **Plages nommées fragiles**, non validables à froid | `named_range_file.html` |
| S15 | **Objets typés limités aux canaux** : « Currently, the only objects that can be typed are channels » | `using_security_policy_types.html` |

---

## 3. Périmètre

### 3.1 Dans le périmètre

- Parseur du langage de politique QNX (types, attributs, classes, règles, plages, plages nommées, `default_spawn_type`, `gain_priv`, `settypeid`).
- Modèle en mémoire : graphe orienté des sujets, types, attributs, classes et règles.
- **Accessibilité** : chemins transitifs de privilège entre deux types, avec contre-exemple rejouable pas à pas.
- **Certificat de non-interférence** : preuve qu'aucune suite d'opérations autorisées ne permet à un type source d'atteindre un type cible.
- **Minimisation** : règles mortes, règles redondantes, règles dominées ; résultat prouvé équivalent sur un corpus de décisions.
- **Typage complet** : détection des processus non typés, cohérence de `default_spawn_type`.
- **Diff sémantique** entre deux politiques : élargissements et réductions de privilège, nouveaux types, règles supprimées.
- **Lint** : abilities sur-dimensionnées, points d'attachage trop larges, règles en contradiction avec un concept de sûreté déclaré, plages nommées non valides à froid.
- Sorties : texte, JSON, Markdown (pour dossier d'audit), HTML (graphe), code de retour non nul en CI.

### 3.2 Hors périmètre (assumé)

Générer une politique (`secpolgenerate` le fait) ; surveiller en temps réel (`secpolmonitor` le fait) ; compiler (`secpolcompile` le fait) ; produire une matrice attaque/mitigation (`security_matrix` le fait) ; analyser du code source ; modifier le noyau ou `procnto` ; couvrir les abilities dynamiques personnalisées non documentées.

---

## 4. Architecture

```
tamis/
├── CONTRACT.md              # contrat gelé : grammaire acceptée, modèle, codes de verdict, formats de sortie
├── core/                    # C11 portable PUR : ni horloge, ni fichier, ni socket, ni allocation non maîtrisée
│   ├── include/tamis/       #   lex.h ast.h model.h reach.h proof.h minimize.h diff.h lint.h report.h
│   ├── src/                 #   lex.c ast.c model.c reach.c proof.c minimize.c diff.c lint.c report.c
│   └── tests/               #   test_lex.c test_ast.c test_model.c test_reach.c test_proof.c
│                            #   test_minimize.c test_diff.c test_lint.c test_util.c
├── host/                    # Python 3 stdlib : tamis (CLI), tamis-ci (passerelle CI), tamis-view (HTML)
├── fixtures/                # corpus de politiques : minimales, réalistes (400+ règles), fautives, de référence
├── oracle/                  # harnais de test différentiel contre secpolcompile (hôte) — optionnel sans SDP
├── tests/                   # différentiel C ↔ Python, fuzz du parseur, banque de cas fautifs, mutants
├── codelab/                 # 4 chapitres : « auditer une politique de sécurité QNX »
└── docs/                    # spec-fr.md, spec-en.md, GRAMMAR.md, DECISIONS.md, VALIDATION.md, AUDIT-TEMPLATE.md
```

**Règle de portabilité.** `core/` ne lit aucun fichier et ne consulte aucune horloge : l'appelant fournit le texte et les tampons. Le même noyau d'analyse est donc exécutable depuis Python, depuis un test unitaire, et plus tard depuis une ligne de build. La double implémentation (C dans `core/`, Python dans `host/`) n'est pas une duplication : c'est un **jumeau de vérification** indépendant, comme sur Ambre et Passerelle.

---

## 5. Contrat

### 5.1 Chaîne de traitement (figée)

```
texte politique → lex → ast → model(graphe) → {reach, proof, minimize, diff, lint} → verdicts → rapport
```

Aucune étape ne remonte : un moteur ne relit jamais le texte. Toute erreur d'analyse arrête la chaîne et produit un verdict `PARSE_ERROR` avec position (ligne, colonne) et cause — **jamais** de reprise approximative sur une politique partiellement comprise.

### 5.2 Verdicts (authoritative : `core/include/tamis/report.h`)

`TAMIS_OK`, `TAMIS_PARSE_ERROR`, `TAMIS_UNTYPED_PROCESS`, `TAMIS_MISSING_DEFAULT_SPAWN`, `TAMIS_DEAD_RULE`,
`TAMIS_REDUNDANT_RULE`, `TAMIS_OVERBROAD_ABILITY`, `TAMIS_RANGE_INVALID`, `TAMIS_PATH_FOUND`,
`TAMIS_INTERFERENCE_POSSIBLE`, `TAMIS_PRIVILEGE_WIDENED`, `TAMIS_PRIVILEGE_NARROWED`, `TAMIS_INCONSISTENT`.

Chaque verdict porte : code, sévérité (`error|warning|info`), position dans le fichier, règle(s) concernée(s), et **chemin complet** quand il s'agit d'un chemin de privilège.

### 5.3 Rapport JSON (une ligne par verdict)

```json
{"code":"TAMIS_PATH_FOUND","sev":"error","src":"type:app_tiers","dst":"type:pompe_critique",
 "hops":3,"path":["app_tiers","journal","diag","pompe_critique"],"rules":["R112","R87","R9"],"file":"policy.secpol","line":214}
```

### 5.4 Sortie d'audit (Markdown, pour dossier de certification)

Une section par propriété vérifiée, avec : énoncé de la propriété, méthode, corpus, résultat, contre-exemple le cas échéant, version de la politique (empreinte SHA-256 du fichier analysé), horodatage, version de Tamis.

---

## 6. Exigences

| ID | Niveau | Exigence | Vérification |
|---|---|---|---|
| TAM-01 | S | La grammaire acceptée est écrite dans `docs/GRAMMAR.md` à partir de la documentation officielle, avec pour chaque production la page source | revue croisée avec `secpol_language.html` |
| TAM-02 | S | Le parseur accepte le corpus de fixtures et **refuse** toute entrée hors grammaire avec position et cause ; aucune analyse partielle silencieuse | 40 politiques fautives, chacune avec l'erreur attendue |
| TAM-03 | S | Le modèle construit est fidèle : types, attributs, classes, règles, plages, `default_spawn_type`, `gain_priv`, `settypeid` | tests sur fixtures minimales |
| TAM-04 | S | L'accessibilité transitive trouve un chemin entre deux types et restitue le chemin complet (types intermédiaires + règles) | fixtures dirigées, 12 cas |
| TAM-05 | S | L'absence de chemin est **prouvée**, pas seulement non trouvée : parcours exhaustif avec compteur de visites publié | test sur graphe acyclique et sur graphe à cycles |
| TAM-06 | S | Le lint détecte les processus non typés et l'absence de `default_spawn_type` (trous S7, S10) | fixtures dirigées |
| TAM-07 | S | La minimisation retire les règles mortes et dominées, et **prouve** l'équivalence : même verdict sur un corpus de 10 000 requêtes de décision avant/après | test d'équivalence |
| TAM-08 | S | Le diff sémantique signale tout élargissement de privilège entre deux politiques, avec la règle responsable | fixtures paire avant/après |
| TAM-09 | S | Le jumeau Python et le cœur C donnent des verdicts identiques ; désaccord réduit dichotomiquement jusqu'à la requête fautive | test différentiel par graine |
| TAM-10 | S | CI ≤ 5 min par job, `fetch-depth: 1`, `concurrency` ; gardes de taille, de licence et de budget | garde `ci-budget`, `sizecheck.py` |
| TAM-11 | S | Le parseur est fuzzé (entrées déterministes par graine) sans crash ni fuite sous ASan/UBSan | 200 000 entrées |
| TAM-12 | C | Test différentiel contre `secpolcompile` : toute politique acceptée par Tamis est acceptée par le compilateur officiel, et inversement | `oracle/` (nécessite le SDP hôte) |
| TAM-13 | C | Les plages nommées sont validées à froid : existence, disjonction, couverture attendue, bornes (trou S13) | fixtures de plages |
| TAM-14 | C | Le graphe `settypeid` / `gain_priv` est analysé : cycles, élévations atteignables, contre-exemple rejouable (trou S8) | fixtures dirigées |
| TAM-15 | C | Croisement avec `/dev/secpolgenerate/unused` et `/errors` quand ces fichiers sont fournis : les règles signalées inutilisées sont candidates à suppression, avec justification | test sur fichiers de référence |
| TAM-16 | C | Rapport Markdown de certification exploitable tel quel par un auditeur, avec empreinte de la politique analysée | relecture à froid |
| TAM-17 | C | Intégration CI : `tamis-ci` commente une demande de fusion avec le diff sémantique et bloque sur élargissement de privilège | démonstration sur une PR |
| TAM-18 | C | Fusion à trois voies assistée : base / généré / édité à la main, conflits signalés, patch réversible (trou S9) | test de fusion |
| TAM-19 | C | Stabilisateur : N politiques générées sont alignées par clé sémantique (sujet + type + ability) et fusionnées en une politique canonique, avec rapport de variance (trou S6) | test sur corpus instable |
| TAM-20 | X | Preuve de non-interférence formalisée et exportable : énoncé, hypothèses, méthode, résultat, contre-exemple — format compatible dossier de sécurité | revue par un agent neuf |
| TAM-21 | X | Analyse des angles morts déclarés par la doc (trou S4) : permissions de fichiers, transitions root→non-root — Tamis les signale comme **non couverts** au lieu de les ignorer | rapport d'angles morts |
| TAM-22 | X | Extension du modèle aux objets non-canaux (trou S15), en anticipation : mémoire partagée, connexions | prototype + note de conception |
| TAM-23 | X | Visualiseur HTML du graphe de privilèges, filtrable, avec surbrillance du contre-exemple | démo |
| TAM-24 | X | Contribution amont : proposition d'un chapitre d'audit ou d'un outil de revue au dépôt QNX concerné | URL de la demande |

---

## 7. Plan de vérification

1. **Unitaires C** : un binaire par module (`test_lex`, `test_model`, `test_reach`, `test_proof`, `test_minimize`, `test_diff`, `test_lint`), retour 0 si vert, `OK <n> checks` en fin. Cible : ≥ 800 vérifications.
2. **Différentiel C ↔ Python** : deux implémentations indépendantes de chaque moteur ; comparaison par graine sur des politiques générées aléatoirement mais valides ; réduction dichotomique du premier désaccord.
3. **Différentiel contre l'oracle officiel** (TAM-12) : `secpolcompile` accepte/refuse — Tamis doit être d'accord. C'est la preuve la plus forte disponible, et elle ne demande **aucune cible**.
4. **Banque de cas fautifs** : 40 politiques invalides, 12 chemins de privilège dirigés, 8 paires avant/après, 6 jeux de plages nommées cassés.
5. **Fuzz** du parseur sous ASan/UBSan.
6. **Mutants** : au moins 10 mutations des moteurs (ordre des règles, sens d'une arête, défaut du refus, borne de plage, compteur de visites) — chacune doit être tuée.
7. **Équivalence de minimisation** : 10 000 requêtes de décision rejouées avant/après, aucune divergence admise.
8. **Gardes maison** : `sizecheck.py` (< 500 lignes/fichier, < 50 lignes/fonction), `spdx-guard`, `ci-budget`.

---

## 8. CI

- `timeout-minutes: 5` par job, `concurrency` avec annulation des runs obsolètes, `actions/checkout@v4` en `fetch-depth: 1`.
- Jobs parallèles : `core` (unitaires C + ASan/UBSan + mutants), `python` (jumeau + différentiel + CLI), `fuzz` (campagne courte bornée en temps).
- Job `oracle` **hors PR**, sur déclenchement manuel, uniquement sur un hôte ayant le SDP : test différentiel contre `secpolcompile`.
- Aucun build pour cible : Tamis est un outil hôte, ce qui rend sa CI entièrement portable.

---

## 9. Jalons

### 9.1 Option 5 semaines (soumission au concours)

| Semaine | Livrable |
|---|---|
| S1 | E1–E5 tranchés ; `docs/GRAMMAR.md` gelé ; `CONTRACT.md` gelé ; parseur + modèle + tests sur fixtures |
| S2 | Accessibilité + preuve d'absence de chemin + lint ; jumeau Python ; test différentiel ; banque de cas fautifs |
| S3 | Minimisation avec preuve d'équivalence ; diff sémantique ; rapport Markdown d'audit |
| S4 | Plages nommées, graphe `gain_priv`, fusion à trois voies, stabilisateur ; fuzz et mutants ; `tamis-ci` |
| S5 | Test différentiel contre `secpolcompile` (si SDP), codelab, docs EN/FR, vidéo 3 min, dépôt public, formulaire |

Ce projet est **le seul du top 7 à pouvoir être terminé et démontré sans aucune cible QNX**. C'est le choix rationnel si la licence tarde.

### 9.2 Option 3 mois

M1 = parseur, modèle, accessibilité, preuve, lint, différentiel C ↔ Python, corpus. M2 = minimisation prouvée, diff sémantique, rapports d'audit, intégration CI, fusion à trois voies, stabilisateur, oracle `secpolcompile`. M3 = angles morts documentés, extension aux objets non-canaux, visualiseur HTML, codelab étendu, contribution amont, validation sur une politique réelle de plusieurs centaines de règles.

---

## 10. Essais de faisabilité (semaine 1, avant tout code produit)

| ID | Question | Comment trancher | Bloquant si |
|---|---|---|---|
| E1 | Quelle est la grammaire exacte du langage de politique ? | Lire intégralement `secpol_language.html`, `using_security_policy_types.html`, `named_range_file.html`, `using_security_policies.html` ; écrire `docs/GRAMMAR.md` avec la page source de chaque production | **oui** : sans grammaire fiable, tout le reste est du sable |
| E2 | `secpolcompile` s'exécute-t-il sur l'hôte et que produit-il exactement ? | Installer le SDP (hôte seul suffit), lancer `secpolcompile` sur une politique d'exemple, inspecter les sorties et l'option de génération d'événements | non : se priver de TAM-12, le reste tient |
| E3 | Existe-t-il une politique d'exemple publique à utiliser comme fixture réaliste ? | Chercher dans le SDP, dans `gitlab.com/qnx/projects`, dans la doc (`mkqnximage` mode démo sécurité) ; à défaut, générer avec `secpolgenerate` sur QEMU | non : écrire un corpus synthétique de 400 règles |
| E4 | Le mode diff de `secpolgenerate` rend-il une sortie exploitable par Tamis ? | Lire `security_policy_maintenance.html` et tester ; sinon, Tamis fait son propre diff entre deux fichiers de politique | non |
| E5 | L'IDE Momentics contient-il un éditeur ou un analyseur de politique ? | Parcourir le sommaire du guide de l'IDE (chapitres connus : développement, débogage, tests unitaires, mémoire, performance, comportement système, construction d'images, JTAG) et chercher « secpol », « policy » | **oui** : si un analyseur existe, le projet perd son innovation |

---

## 11. Risques

| Risque | Probabilité | Impact | Parade |
|---|---|---|---|
| La grammaire a des recoins non documentés | moyenne | fort | Mode « sous-ensemble strict » : Tamis refuse d'analyser ce qu'il ne sait pas parser, et le dit. Jamais d'analyse approximative |
| `secpolcompile` indisponible sans licence | faible | moyen | TAM-12 est optionnel ; le différentiel C ↔ Python reste la preuve principale |
| Un outil QNX non documenté fait déjà de l'analyse | faible | fort | Essai E5, puis question directe sur le Discord QNX et r/qnx |
| La preuve de non-interférence est jugée trop théorique par les juges | moyenne | moyen | Toujours l'accompagner d'un contre-exemple concret et d'un chiffre (400 règles → 212, comportement identique) |
| Politique réelle trop grosse pour un corpus public | faible | faible | Corpus synthétique généré, plus la politique de démonstration de `mkqnximage` |
| Les objets typés se limitent aux canaux, donc la portée de l'analyse est bornée | certaine | moyen | Le dire explicitement dans la soumission ; TAM-22 prépare l'extension |

---

## 12. Script vidéo (3 minutes)

| Temps | Plan |
|---|---|
| 0:00–0:20 | La doc QNX : « la politique générée n'est pas utilisable telle quelle », « la revue des règles inutiles est manuelle », « aucune analyse avant déploiement ». Trois citations, trois trous |
| 0:20–0:50 | `tamis lint policy.secpol` sur une politique de 400 règles : 88 règles mortes, 3 abilities sur-dimensionnées, 2 processus non typés |
| 0:50–1:40 | `tamis reach --src app_tiers --dst pompe_critique` : chemin en 3 sauts affiché, règles citées, ligne dans le fichier. On coupe la règle fautive, on relance : plus de chemin, **certificat de non-interférence** vert |
| 1:40–2:10 | `tamis minimize` : 400 → 212 règles, et la preuve d'équivalence (10 000 décisions identiques, aucune divergence) |
| 2:10–2:40 | `tamis diff v1.secpol v2.secpol` dans une PR : un élargissement de privilège signalé, la CI passe au rouge, commentaire automatique |
| 2:40–3:00 | Les preuves : nombre de vérifications, mutants tués, fuzz, différentiel C ↔ Python, et (si disponible) accord avec `secpolcompile` |

---

## 13. Dossier de soumission Devpost

1. **Dépôt public** créé pendant la période de soumission, licence ouverte visible en tête de page (Apache-2.0 ou MIT).
2. **Catégorie** : Developer Tooling & Host Tools. Éligible au titre d'« outil hôte qui analyse du logiciel destiné à QNX 8.0 ».
3. **Preuve d'usage de QNX** (obligatoire, à rédiger avec soin — c'est le point sensible d'un outil hôte) : citer nommément le langage de politique QNX et ses fichiers, `core/src/lex.c` et `model.c` qui implémentent la grammaire QNX avec les pages de doc en référence, `oracle/` qui exécute `secpolcompile`, `fixtures/` contenant des politiques QNX réelles, `image/` montrant l'insertion de la politique analysée dans une image QNX, et la démonstration vidéo sur une politique destinée à QNX 8.0.
4. **Description** : les trous cités de la documentation officielle → ce que Tamis ajoute (analyse à froid, preuve, minimisation, diff) → la frontière explicite avec `secpolgenerate`/`secpolcompile`/`secpolpush`/`secpolmonitor` → les preuves (tests, mutants, fuzz, oracle) → la reproductibilité.
5. **Instructions de build et d'exécution** : version de QNX visée (SDP 8.0), outils requis, commandes exactes, jeu de données d'exemple.
6. **Bonus** : cocher **Best use of QNX-specific Technologies** (politiques de sécurité explicitement citées par le règlement) et **Best Codelab/Tutorial** avec l'URL du codelab en 4 chapitres.
7. **Langue** : anglais, ou traduction anglaise fournie.

---

## 14. Statut des affirmations

**Vérifié dans la documentation** (pages lues) : existence et rôle de `secpolgenerate` (dont le **mode diff incrémental**), `secpolcompile` (utilitaire **hôte**), `secpolpush`, `secpolmonitor`, `libsecpol`, `libsecpolev` ; existence de `/dev/secpolgenerate/errors` et `/unused` ; les 11 trous listés en section 2.2, chacun avec sa page source ; environ 70 abilities statiques plus des abilities dynamiques personnalisées ; Pathtrust et fonctions fortifiées ; `security_matrix` ; absence de tout outil d'analyse de politique dans les chapitres connus du guide de l'IDE Momentics.

**Non vérifié — à faire en S1** : la **grammaire exacte** du langage de politique (`secpol_language.html` n'a pas été lu page à page) ; le contenu de `named_range_file.html` ; la sortie exacte de `secpolcompile` et son option de génération d'événements ; l'existence ou non d'une politique d'exemple publique ; l'absence d'un analyseur de politique dans les chapitres de l'IDE non encore lus (essai E5).

**Volontairement non affirmé** : aucune capacité à analyser les abilities dynamiques personnalisées non documentées ; aucune prétention à couvrir les angles morts que la documentation attribue à `secpolgenerate` (trou S4) — Tamis les **signale** comme non couverts (TAM-21), il ne les résout pas.

---

## 15. Règles de code et délégation

**Règles maison** : C11, `-std=c11 -O2 -Wall -Wextra -Werror` ; `core/` pur — ni horloge, ni fichier, ni socket, ni état global mutable, l'appelant fournit texte et tampons ; moins de 500 lignes par fichier, moins de 50 lignes par fonction, découper plutôt que laisser grossir ; **aucune duplication** — le jumeau Python est une implémentation indépendante assumée et documentée comme telle, pas une copie du C ; Python 3 standard uniquement ; chaque exigence citée en commentaire au-dessus du code et dans le nom du test correspondant.

**Découpage en lots pour sous-agents** :

| Lot | Contenu | Dépend de |
|---|---|---|
| L0 | Lecture des 4 pages de doc, rédaction de `docs/GRAMMAR.md` et gel de `CONTRACT.md` | — |
| L1 | `core/` lex + ast + tests + banque de 40 politiques fautives | L0 |
| L2 | `core/` model (graphe) + tests sur fixtures minimales | L1 |
| L3 | `core/` reach + proof (avec preuve d'absence) + tests dirigés | L2 |
| L4 | `core/` lint (typage, `default_spawn_type`, abilities sur-dimensionnées) | L2 |
| L5 | Jumeau Python (lex, model, reach, lint) + test différentiel + réduction dichotomique | L3, L4 |
| L6 | `core/` minimize + preuve d'équivalence sur 10 000 décisions | L3 |
| L7 | `core/` diff sémantique + `tamis-ci` + rapport Markdown d'audit | L6 |
| L8 | Plages nommées + graphe `gain_priv` + fusion à trois voies + stabilisateur | L7 |
| L9 | Fuzz + mutants + gardes (sizecheck, spdx, ci-budget) | L1–L8 |
| L10 | `oracle/` : différentiel contre `secpolcompile` (nécessite le SDP hôte) | E2 |
| L11 | Codelab 4 chapitres + docs EN/FR + script vidéo + visualiseur HTML | L1–L9 |

Chaque brief de sous-agent rappelle : contexte complet (aucune mémoire partagée), critère de succès mesurable, bornes (temps, nombre d'essais, comportement en cas d'échec), règles shell (jamais `node -e`, `timeout` devant les commandes longues), et « fais-le toi-même, sans déléguer ».
