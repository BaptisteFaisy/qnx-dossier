# 100 idées — QNX Global Hackathon 2026 (recalibrées 3 mois)

Chaque idée cite le trou documenté qu'elle exploite (voir qnx-inventaire-officiel.md)
ou une absence vérifiée dans l'index officiel github.com/qnx-ports/build-files/ports.

Légende : SDP = le SDK installé est-il requis (oui/non/partiel).
Provenance : lot A par sous-agent (texte complet restauré), lots B à F par b.

## Lot A — Sécurité et politiques (15 trous du System Security Guide)

1. **Éplucheur** — Developer Tooling & Host Tools | Gap : 1 | Assistant de purge qui croise `/dev/secpolgenerate/unused`, les compteurs d'usage et un rejeu scénarisé pour classer chaque règle (utilisée / douteuse / morte) et produire un plan de suppression ordonné, chiffré et réversible au lieu de la revue manuelle prescrite par la doc | SDP : partiel (moteur d'analyse C11 + corpus de politiques sur PC, génération et compteurs sur cible) | Effort 5 sem : moyen | Démo : politique de 900 règles ramenée à 300 avec rapport de preuve ligne à ligne | Originalité : 4
2. **Durcisseur** — Low-level Software | Gap : 2 | Post-processeur qui rend la sortie brute de `secpolgenerate` directement exploitable : normalisation, en-têtes manquants, découpe en fichiers inclus, passage systématique par `secpolcompile` et paquet prêt pour `secpolpush`/`mkqnximage` | SDP : partiel (chaîne de transformation testable sur PC avec des échantillons, compilation sur cible) | Effort 5 sem : faible | Démo : un seul `make image` du log brut à l'image QNX qui démarre sans erreur | Originalité : 3
3. **Oracle** — Developer Tooling & Host Tools | Gap : 3 | Analyseur statique de politique : parse la sortie, construit le graphe sujets/types/abilities et répond avant tout déploiement à « cette règle est-elle atteignable, sur-permissive, en conflit ? » avec simulation de décision hors ligne | SDP : oui (cœur C11 pur, corpus de politiques versionné, tests unitaires sur PC) | Effort 5 sem : moyen | Démo : détection en pré-exécution d'une faille que le déploiement réel ne révélerait qu'au bout d'une semaine | Originalité : 5
4. **Témoin** — Low-level Software | Gap : 4 | Sonde de couverture qui rend visibles les angles morts du générateur : wrapper d'exécution journalisant chmod, setuid/setgid, transitions root→non-root et permissions de fichiers, corrélé à la politique pour lister les trous que `secpolgenerate` ne pouvait pas voir | SDP : partiel (corrélateur C11 sur PC, capture système sur cible) | Effort 5 sem : moyen | Démo : rapport « 7 échecs invisibles trouvés, 4 corrigés par règle ajoutée » sur une appli réelle | Originalité : 4
5. **Filtre** — Developer Tooling & Host Tools | Gap : 5 | Trieur de faux positifs : base de connaissances des erreurs setuid/setgid/prot_exec/priority, classées « contournable sans noyau » vs « exige `procnto` », avec recette de substitution par motif (spawn flags, abilities, ordonnancement) et rapport d'exclusion assumé | SDP : oui (moteur de règles + base de connaissances en C11 sur PC, motifs d'entrée réels collectés) | Effort 5 sem : faible | Démo : pile de 40 erreurs de génération réduite à 3 blocages réels documentés | Originalité : 3
6. **Empreinte** — Low-level Software | Gap : 6 | Stabilisateur de génération : N exécutions du même scénario, alignement des règles par clé sémantique (sujet + type + ability), fusion en politique canonique minimisée et rapport de variance expliquant ce qui oscille d'un run à l'autre | SDP : oui (alignement et fusion en C11 sur PC à partir de jeux de politiques fournis) | Effort 5 sem : moyen | Démo : trois runs divergents convergent en une politique identique bit à bit | Originalité : 4
7. **Amorce** — Developer Tooling & Host Tools | Gap : 7 | Générateur du `default_spawn_type` manquant : infère le type par défaut par binaire depuis l'empreinte d'exécution et le chemin, émet le fragment à recoller et vérifie qu'aucun processus ne se retrouve non typé par accident | SDP : partiel (inférence et vérification sur PC, collecte sur cible) | Effort 5 sem : faible | Démo : politique incomplète devenue complète sans édition manuelle, `pidin` à l'appui | Originalité : 3
8. **Grimpeur** — Low-level Software | Gap : 8 | Moteur formel d'analyse d'élévation de privilèges qui remplace l'essai-erreur prescrit : graphe `settypeid`/`gain_priv`, recherche de chemins, détection de cycles, score de criticité et contre-exemple rejouable pas à pas | SDP : oui (graphe et recherche en C11, validés sur des topologies synthétiques puis réelles) | Effort 5 sem : moyen | Démo : découverte d'une chaîne d'élévation à 4 sauts sur une politique d'exemple, avec trace | Originalité : 5
9. **Tisserand** — Developer Tooling & Host Tools | Gap : 9 | Fusionneur automatique après diff incrémental : merge à trois voies (base / généré / édité à la main), résolution de conflits par règles de priorité déclarées, patch signé, réversible et intégrable à git | SDP : oui (merge C11 sur PC, jeux de politiques en entrée) | Effort 5 sem : moyen | Démo : mise à jour de l'appli qui régénère la politique sans perdre une seule règle écrite à la main | Originalité : 4
10. **Contrôleur** — Low-level Software | Gap : 10 | Vérificateur de typage complet : sonde périodique qui remplace le `pidin -f a_n…` manuel, classe les processus non typés, alerte en CI et audite l'image produite par `mkqnximage` avant flash | SDP : partiel (moteur d'audit et hook CI sur PC, interrogation runtime sur cible) | Effort 5 sem : faible | Démo : pipeline qui refuse une image où 3 processus ont échappé au typage | Originalité : 3
11. **Écouteur** — Open-Source Contribution & Ports | Gap : 11 | Client open-source de `libsecpolev` : chargement explicite de la bibliothèque verrouillée non auto-découverte, normalisation du flux en JSON/OpenTelemetry et tableau de bord temps réel des violations exploitable hors de QNX | SDP : partiel (normaliseur et dashboard sur PC, source d'événements sur cible ou en rejou) | Effort 5 sem : moyen | Démo : violation de politique visible en direct dans un navigateur à 500 ms près | Originalité : 4
12. **Navette** — Developer Tooling & Host Tools | Gap : 12 | Boucle de développement chaude : démon qui surveille le fichier de configuration de `secpolgenerate`, relance génération et compilation, pousse et affiche le delta de violations en quelques secondes, plus un REPL pour tester une règle avant de l'écrire | SDP : partiel (orchestrateur et REPL sur PC, déploiement sur cible ou QEMU) | Effort 5 sem : faible | Démo : édition d'une règle, sauvegarde, verdict de sécurité affiché en moins de 10 s | Originalité : 3
13. **Jauge** — Low-level Software | Gap : 13 | Validateur de plages nommées à froid : existence, disjonction, couverture attendue et tests de bornes générés automatiquement, pour que plus aucune plage fragile ne parte en production sans preuve | SDP : oui (validateur et générateur de tests C11 sur PC, definitions de plages en entrée) | Effort 5 sem : faible | Démo : chevauchement de deux plages détecté avant déploiement, avec cas limite rejoué | Originalité : 4
14. **Miroir** — Low-level Software | Gap : 14 | Auto-hébergement de la surveillance : une seconde instance de `secpolgenerate` typée différemment surveille la première, un arbitre compare les deux flux et journalise la surveillance du surveillant dans une chaîne de confiance mesurée | SDP : non (besoin des deux instances sur cible ou QEMU ; arbitre et comparateur en C11 testables sur PC) | Effort 5 sem : élevé | Démo : corruption du générateur principal détectée en direct par son miroir | Originalité : 5
15. **Mouleur** — Low-level Software | Gap : 15 | Couche de typage au-delà des canaux : gestionnaire de ressources qui applique le même modèle de types et d'abilities aux mémoires partagées et aux connexions, avec bibliothèque cliente et expression de politique dans la syntaxe existante | SDP : partiel (modèle de typage et bibliothèque sur PC, gestionnaire de ressources sur cible) | Effort 5 sem : élevé | Démo : partage mémoire refusé à un processus non habilité, politique inchangée ailleurs | Originalité : 4
16. **Sillage** — Automotive & Mobility | Gap : 3 | Dossier de validation pour calculateur : analyse statique de politique, preuve de non-élévation et journal horodaté des violations exportés comme artefact d'homologation aligné ISO 21434 / UNECE R155 | SDP : oui (génération du dossier et preuves sur PC, mesures embarquées ensuite) | Effort 5 sem : moyen | Démo : export d'un dossier d'audit complet signé depuis un simple build de politique | Originalité : 4
17. **Perfuseur** — Robotics & Medical | Gap : 11 | Garde-fou temps réel pour robot ou dispositif médical : flux `libsecpolev` normalisé branché sur un superviseur qui bascule l'actionneur en mode sûr dès qu'une ability critique est violée, avec latence bornée mesurée et publiée | SDP : partiel (superviseur et rejou d'événements sur PC, boucle temps réel sur QEMU ou Pi 5) | Effort 5 sem : élevé | Démo : bras robotisé immobilisé en moins d'une milliseconde après violation de politique | Originalité : 4

## Lot B — Outillage temps réel, trace et supervision (5 trous des Utilities)

1. **Pendule** — Developer Tooling | Gap : 3 | L'équivalent `cyclictest` qui manque : mesure de latence IRQ→thread et de réveil de thread sur N priorités, avec p50/p99/p99.9/max publiés. | SDP : non (mesure sur cible, agrégation sur PC) | Effort : moyen | Démo : courbe de latence sous charge, pire cas affiché | Originalité : 4
2. **Flamme** — Developer Tooling | Gap : 1 | Profileur par échantillonnage sans noyau instrumenté ni IDE : piles échantillonnées via l'API d'introspection, agrégées en flame graph côté hôte. | SDP : partiel | Effort : élevé | Démo : flame graph d'une image QNX réelle | Originalité : 4
3. **Loupe** — Developer Tooling | Gap : 2 | Agrégateur de trace : transforme le texte brut de `traceprinter` en histogrammes de latence, statistiques par priorité et frise HTML. | SDP : oui (parseur sur PC, traces enregistrées) | Effort : faible | Démo : trace brute → rapport HTML en une commande | Originalité : 3
4. **Échéancier** — Developer Tooling | Gap : 3 | Détection d'échéance manquée : le développeur déclare période et budget, l'outil vérifie chaque cycle sur trace et nomme le responsable (interruption, thread plus prioritaire). | SDP : oui | Effort : moyen | Démo : une échéance violée, coupable désigné | Originalité : 5
5. **Renverse** — Developer Tooling | Gap : 3 | Détecteur d'inversion de priorité : reconstruit les chaînes d'attente (mutex, `MsgSend` bloquant) et prouve si l'héritage de priorité a fonctionné. | SDP : oui | Effort : moyen | Démo : inversion provoquée puis corrigée, avant/après | Originalité : 4
6. **Déclic** — Developer Tooling | Gap : 4 | Enregistreur circulaire qui se fige au crash : surveille la terminaison, arrête la trace, sauve tampon + `pidin` + `slog2` dans une archive horodatée unique. | SDP : partiel | Effort : moyen | Démo : un processus tué, archive complète produite | Originalité : 4
7. **Autopsie** — Developer Tooling | Gap : 4 | Analyseur post-mortem corrélé : ouvre l'archive, croise vidange `dumper` et tampon de trace, reconstitue la chaîne de blocage et désigne le coupable. | SDP : oui (analyseur sur PC) | Effort : élevé | Démo : interblocage expliqué en une page | Originalité : 5
8. **Compteur** — Developer Tooling | Gap : 5 | Comptabilité d'E/S par processus et par gestionnaire de ressources (`sar`/`iostat` manquants) : débits, tailles, temps de service, files. | SDP : non | Effort : moyen | Démo : tableau des services les plus coûteux | Originalité : 3
9. **Pouls** — Developer Tooling | Gap : 5 | Vue temps réel côté hôte : flux depuis la cible, par priorité/classe/cœur, historique et seuils. | SDP : non | Effort : moyen | Démo : dashboard live sous QEMU | Originalité : 2 (concurrence de `pidin`/`hogs`)
10. **Sismographe** — Developer Tooling | Gap : 3 | Banc de régression temps réel en CI : scénario de charge standardisé à chaque PR, dérive des percentiles publiée, seuil rouge. | SDP : partiel | Effort : moyen | Démo : PR rouge pour 40 µs de dérive p99.9 | Originalité : 4
11. **Étalon** — Developer Tooling | Gap : 3 | Jeu de charges normalisées reproductibles (rafale de messages, tempête d'interruptions, famine mémoire) avec rapport chiffré : le `stress-ng` du temps réel. | SDP : oui (générateur portable) | Effort : moyen | Démo : même image, deux machines, chiffres comparables | Originalité : 4
12. **Filature** — Developer Tooling | Gap : 4 | Reconstructeur de causalité des messages : graphe des connexions et journal des allers-retours avec latences, export JSON. | SDP : oui | Effort : moyen | Démo : graphe de qui-parle-à-qui d'une image | Originalité : 3
13. **Bilan** — Developer Tooling | Gap : 1 | Coût CPU par gestionnaire de ressources sans PMU : attribution par événements de trace, ventilée par type de message. | SDP : oui | Effort : moyen | Démo : facture CPU par service | Originalité : 3
14. **Sentinelle** — Developer Tooling | Gap : 2 | Alertes de trace en continu : règles déclaratives (file saturée, thread affamé, priorité inversée) déclenchant une capture immédiate. | SDP : non | Effort : moyen | Démo : alerte → archive automatique | Originalité : 4
15. **Rapport** — Developer Tooling | Gap : 1 à 5 | Générateur de rapport de performance horodaté et diffable agrégeant trace, `pidin` et `slog2`, utilisable en dossier d'homologation. | SDP : oui | Effort : faible | Démo : rapport signé entre deux versions | Originalité : 2
16. **Réplique** — Developer Tooling | Gap : 4 | Rejeu déterministe d'une trace dans un simulateur d'ordonnanceur : reproduire un bogue de concurrence sans la cible. | SDP : oui | Effort : élevé | Démo : bogue rejoué à l'identique sur PC | Originalité : 5
17. **Veilleur** — Developer Tooling | Gap : 5 | Agent de surveillance embarqué à empreinte bornée publiant en PPS les indicateurs d'E/S, mémoire et ordonnancement. | SDP : non | Effort : moyen | Démo : indicateurs live depuis l'invité | Originalité : 3

## Lot C — Image système, amorçage et mise à jour (5 trous d'OS Components)

1. **Sceau** — Developer Tooling | Gap : 1 | Chaîne de signature et vérification d'image : signe l'IFS et les partitions, vérifie au démarrage via un gestionnaire de ressources, refuse une image altérée. | SDP : partiel | Effort : élevé | Démo : octet modifié → démarrage refusé | Originalité : 4
2. **Cachet** — Developer Tooling | Gap : 1 | Empreinte reproductible et SBOM : deux constructions sur machines différentes donnent la même empreinte, avec composants et licences. | SDP : oui | Effort : moyen | Démo : deux builds, même SHA-256 | Originalité : 4
3. **Doublure** — Automotive & Mobility | Gap : 2 | Mise à jour transactionnelle A/B avec retour arrière : copie vérifiée, bascule atomique, retour automatique si le nouveau slot ne démarre pas. (Image système complète, pas un journal d'événements : distinct de l'EDR déjà fait.) | SDP : partiel | Effort : élevé | Démo : slot B corrompu → retour sur A | Originalité : 4
4. **Campagne** — Automotive & Mobility | Gap : 2 | Orchestrateur de campagne de mise à jour sur parc : prérequis, cohorte témoin, arrêt si santé dégradée, traçabilité R156. | SDP : oui (orchestrateur hôte) | Effort : moyen | Démo : déploiement stoppé en pleine vague | Originalité : 3
5. **Minutage** — Developer Tooling | Gap : 4 | Instrumentation du temps de démarrage par phase (IPL → startup → script → services) avec graphique en cascade et régression en CI. | SDP : partiel | Effort : moyen | Démo : cascade de boot, phase coupable en rouge | Originalité : 4
6. **Grille** — Developer Tooling | Gap : 5 | Linter de buildfile d'image : entrées manquantes, permissions incohérentes, doublons, chemins invalides, avant `mkifs`. | SDP : oui | Effort : faible | Démo : buildfile fautif, 6 erreurs trouvées | Originalité : 3
7. **Tissage** — Developer Tooling | Gap : 5 | Générateur de buildfile depuis une description déclarative : services, dépendances, ordre de lancement, politique de sécurité. | SDP : oui | Effort : moyen | Démo : YAML → image amorçable | Originalité : 4
8. **Cible** — Developer Tooling | Gap : 3 | Front-end unifié multi-cibles (QEMU, RPi 5, BSP manuel) avec cache et artefacts nommés. | SDP : partiel | Effort : moyen | Démo : une commande, trois cibles | Originalité : 3
9. **Repli** — Developer Tooling | Gap : 2 | Gestionnaire de versions d'image : historique, différentiel binaire, restauration ciblée d'une partition. | SDP : oui | Effort : moyen | Démo : retour à la version n-2 en 10 s | Originalité : 3
10. **Sentier** — Developer Tooling | Gap : 4 | Mesure de l'impact de chaque service sur le temps de démarrage, avec recommandations de parallélisation et de démarrage paresseux. | SDP : partiel | Effort : moyen | Démo : boot passé de 4,1 s à 2,3 s | Originalité : 3
11. **Scellé** — Low-level | Gap : 1 | Amorçage vérifié bout en bout : mesure de l'IFS, scellement d'un secret dans l'état mesuré, refus en cas d'altération. | SDP : non | Effort : élevé | Démo : secret illisible après modification | Originalité : 4
12. **Fantôme** — Developer Tooling | Gap : 3 | Comparateur d'images : contenu, tailles, permissions, dépendances, différences entre deux builds, rapport diffable. | SDP : oui | Effort : faible | Démo : diff de deux images en clair | Originalité : 3
13. **Reconstruction** — Developer Tooling | Gap : 5 | Remplaçant des `mkdinit`/`mkrecfs` disparus en 8.0 : construction et initialisation des répertoires et systèmes de fichiers de démarrage. | SDP : partiel | Effort : moyen | Démo : arborescence créée sans outils manquants | Originalité : 3
14. **Partition** — Low-level | Gap : 2 | Redimensionnement et repartitionnement sûrs (ce que `--update` ne sait pas faire) avec plan de migration et retour arrière. | SDP : non | Effort : élevé | Démo : partition étendue sans perte | Originalité : 3
15. **Crible** — Developer Tooling | Gap : 1 | Vérificateur de conformité d'image avant flash : politique présente, permissions, binaires signés, services déclarés, bloquant en CI. | SDP : oui | Effort : moyen | Démo : image refusée pour politique absente | Originalité : 4
16. **Aube** — Low-level | Gap : 4 | Journal de démarrage structuré et horodaté dès les premières instructions, exploitable côté hôte sans console série. | SDP : partiel | Effort : moyen | Démo : boot sans série, journal récupéré | Originalité : 3
17. **Gabarit** — Developer Tooling | Gap : 3 | Générateur de squelette de projet cible (buildfile, Makefile, script de boot, tests, CI) reproductible en une commande. | SDP : oui | Effort : faible | Démo : projet complet en 30 s | Originalité : 2

## Lot D — Hyperviseur, conteneurs, réseau, graphisme (manques vérifiés)

1. **Veine** — Low-level | Manque : vsock absent des 20 vdev | Pilote virtio-vsock : canal hôte-invité fiable sans pile réseau, avec outil de dialogue côté hôte. | SDP : non | Effort : élevé | Démo : aller-retour hôte-invité en microsecondes | Originalité : 4
2. **Onde** — Low-level | Manque : virtio-snd absent | Pilote audio virtio-snd à tampons périodiques échéancés, avec mesure de gigue de trame. | SDP : non | Effort : élevé | Démo : flux 48 kHz sous charge, zéro tampon raté | Originalité : 4
3. **Main** — Low-level | Manque : virtio-input absent | Pilote virtio-input (clavier, souris, manette) exposé comme périphérique, événements horodatés à la source. | SDP : non | Effort : moyen | Démo : saisie hôte, latence événement-app mesurée | Originalité : 3
4. **Ballon** — Low-level | Manque : virtio-balloon absent | Pilote virtio-balloon : restitution dynamique de mémoire à l'hôte avec politique de priorité par partition. | SDP : non | Effort : élevé | Démo : mémoire rendue sans interrompre la boucle critique | Originalité : 4
5. **Toile** — Low-level | Manque : virtio-gpu absent | Pilote virtio-gpu minimal 2D permettant à Screen de fonctionner en invité sans passthrough matériel. | SDP : non | Effort : élevé | Démo : bureau QNX affiché dans une VM | Originalité : 5
6. **Cloison** — Developer Tooling | Manque : pas de namespace de processus | Visibilité bornée par conteneur : un `pidin`/`ps` qui ne voit que son conteneur, plus un superviseur de fuite. | SDP : partiel | Effort : moyen | Démo : conteneur A aveugle au conteneur B | Originalité : 4
7. **Garde** — Developer Tooling | Manque : pas de confinement root | Confinement root pour conteneurs : politique de sécurité type conteneur + vérificateur statique avant déploiement. | SDP : oui | Effort : moyen | Démo : escalade root refusée et journalisée | Originalité : 4
8. **Écluse** — Developer Tooling | Manque : jail réseau défaillant | Pare-feu de conteneur vérifiable : règles déclaratives, application par politique, tests automatiques de fuite. | SDP : oui | Effort : moyen | Démo : matrice de fuites testée, une trouvée | Originalité : 3
9. **Quic** — Low-level | Manque : module io-sock QUIC absent | Module protocolaire io-sock implémentant un sous-ensemble de QUIC pour échanges à latence bornée. | SDP : non | Effort : élevé | Démo : échange QUIC hôte-invité, perte de paquet injectée | Originalité : 4
10. **Cadence** — Low-level | Manque : TSN/AVB absent | Module io-sock pour planification de trafic TSN (gates 802.1Qbv) et mesure de gigue de bout en bout. | SDP : non | Effort : élevé | Démo : trafic prioritaire non perturbé par la charge | Originalité : 4
11. **Ruche** — Low-level | Manque : protocole capteurs contraints absent | Module io-sock léger pour bus de capteurs contraints, avec qualité de service à échéance. | SDP : non | Effort : moyen | Démo : 200 capteurs simulés, aucune échéance manquée | Originalité : 3
12. **Vitrine** — Developer Tooling | Manque : pas de diffusion d'écran | Diffusion d'un écran QNX vers un navigateur pour démo et télédiagnostic sans matériel ni console. | SDP : partiel | Effort : moyen | Démo : l'invité QNX visible dans le navigateur | Originalité : 3
13. **Compositeur** — Open-Source Ports | Manque : Wayland core seulement | Extensions Wayland manquantes (sous-surfaces, verrouillage, multi-écran) au-dessus de Screen. | SDP : non | Effort : élevé | Démo : deux surfaces composées à cadence garantie | Originalité : 3
14. **Dimensionneur** — Developer Tooling | Manque : allocation mémoire statique des invités | Outil de dimensionnement des partitions d'hyperviseur : mesure de l'usage réel puis proposition d'allocation et de budgets. | SDP : oui | Effort : moyen | Démo : rapport « cette VM gaspille 340 Mo » | Originalité : 3
15. **Simulacre** — Developer Tooling | Manque : testabilité des vdev | Banc de test de vdev sur PC : modèle d'invité factice qui exerce un vdev sans hyperviseur ni cible. | SDP : oui | Effort : moyen | Démo : un vdev testé sur PC avant tout flash | Originalité : 4
16. **Étiquette** — Low-level | Manque : mémoire partagée inter-OS non typée | Couche de mémoire partagée étiquetée et vérifiée (types, tailles, propriétaires) au-dessus du vdev `shmem`. | SDP : oui | Effort : moyen | Démo : échange hôte-invité avec type invalide refusé | Originalité : 4
17. **Surveillant** — Developer Tooling | Manque : supervision des invités | Supervision d'invités sous hyperviseur : santé, budgets, redémarrage, corrélation avec l'hôte. | SDP : partiel | Effort : moyen | Démo : invité planté relancé en 800 ms | Originalité : 3

## Lot E — Ports open source (absences vérifiées dans l'index officiel)

1. **Éclat** — Open-Source Ports | Amont : WAMR (github.com/bytecodealliance/wamr) | Runtime WebAssembly en C + courtier de capacités : exécution bac à sable de code tiers sur un RTOS. Absence vérifiée : aucun port wasm/wamr/wasi dans l'index, `qnx-ports/wamr` en 404. | SDP : partiel (cœur WAMR compilable sur PC) | Effort : moyen | Démo : plugin non fiable chargé à chaud, accès interdit refusé | PR amont : couche QNX + correctifs portabilité | Originalité : 5
2. **Sablier** — Open-Source Ports | Amont : rt-tests / cyclictest (git.kernel.org/pub/scm/utils/rt-tests) | Portage de `cyclictest` et de la suite rt-tests : mesure de latence standardisée et comparable à Linux. Absence vérifiée dans l'index. | SDP : partiel | Effort : moyen | Démo : histogramme de latence max sur 10 min | PR amont : support de cible QNX | Originalité : 4
3. **Écoute** — Open-Source Ports | Amont : API inotify (shim, modèle = port `epoll` officiel) | Shim `inotify` au-dessus de `ionotify` : débloque des milliers de projets POSIX (watchers de build, éditeurs). Seul `epoll` existe aujourd'hui. | SDP : oui | Effort : moyen | Démo : un watcher de fichiers POSIX fonctionne inchangé | PR amont : vers les consommateurs (tokio, libev) | Originalité : 4
4. **Tempo** — Open-Source Ports | Amont : API timerfd (shim) | Shim `timerfd` sur les temporisateurs QNX : complète la famille avec `epoll` déjà porté. | SDP : oui | Effort : faible | Démo : boucle événementielle POSIX inchangée | PR amont : vers tokio/mio | Originalité : 4
5. **Signe** — Open-Source Ports | Amont : API signalfd (shim) | Shim `signalfd` : réception synchrone des signaux dans une boucle événementielle. | SDP : oui | Effort : faible | Démo : signaux traités sans handler asynchrone | PR amont : vers libev/libuv | Originalité : 4
6. **Bobine** — Open-Source Ports | Amont : FFmpeg (ffmpeg.org) | Portage du cœur codec/mux : le multimédia embarqué manque d'un framework, les dépendances image sont déjà portées. | SDP : partiel | Effort : élevé | Démo : transcodage d'un flux sur RPi 5 | PR amont : correctifs de portabilité | Originalité : 3
7. **Pipeline** — Open-Source Ports | Amont : GStreamer (gstreamer.freedesktop.org) | Cadre de pipeline multimédia sur Screen et l'audio QNX, avec chaînage d'éléments à échéance. | SDP : partiel | Effort : élevé | Démo : pipeline vidéo, image ratée comptée | PR amont : backend QNX | Originalité : 3
8. **Souche** — Open-Source Ports | Amont : git (git-scm.com) | git sur QNX : `bash`, `curl`, `libssh2`, `zlib` déjà portés, les dépendances sont prêtes ; utile au développement sur cible auto-hébergée. | SDP : partiel | Effort : moyen | Démo : clone et commit sur l'invité QNX | PR amont : correctifs POSIX | Originalité : 2
9. **Fouille** — Open-Source Ports | Amont : jq (jqlang.github.io/jq) | jq sur QNX : traitement JSON embarqué pour le diagnostic et les scripts d'image. | SDP : oui | Effort : faible | Démo : requête JSON sur `slog2` exporté | PR amont : support de cible | Originalité : 2
10. **Tableau** — Open-Source Ports | Amont : htop (htop.dev) | htop sur QNX : supervision interactive des processus et priorités, complément visuel à `pidin`. | SDP : partiel | Effort : faible | Démo : htop affichant les classes temps réel | PR amont : couche QNX | Originalité : 2
11. **Brique** — Open-Source Ports | Amont : LittleFS (github.com/littlefs-project/littlefs) | Système de fichiers tolérant aux coupures pour flash, exposé comme gestionnaire de ressources QNX. | SDP : oui | Effort : moyen | Démo : coupure pendant écriture, FS intact | PR amont : couche de portage | Originalité : 3
12. **Canette** — Open-Source Ports | Amont : can-utils / libsocketcan (github.com/linux-can) | Couche CAN utilisateur sur QNX avec pilote virtuel pour les tests sans matériel. | SDP : oui | Effort : moyen | Démo : trames CAN entre deux processus QNX | PR amont : backend QNX | Originalité : 3
13. **Modbus** — Open-Source Ports | Amont : libmodbus (libmodbus.org) | Passerelle industrielle à échéances garanties, esclave simulé pour la démo. | SDP : oui | Effort : faible | Démo : interrogation garantie en cadence sous charge | PR amont : support de cible | Originalité : 2
14. **Timbre** — Open-Source Ports | Amont : PortAudio (portaudio.com) | Couche audio portable au-dessus de l'audio QNX pour les applications temps réel. | SDP : partiel | Effort : moyen | Démo : même code audio sur Linux et QNX | PR amont : backend QNX | Originalité : 3
15. **Zen** — Open-Source Ports | Amont : zenoh-pico (github.com/eclipse-zenoh/zenoh-pico) | Pub/sub robotique très léger en C, alternative à DDS déjà porté ; à vérifier sur oss.qnx.com avant engagement. | SDP : oui | Effort : moyen | Démo : deux nœuds QNX à cadence garantie | PR amont : couche QNX | Originalité : 3
16. **Verrou** — Open-Source Ports | Amont : wolfSSL (wolfssl.com) | TLS à empreinte bornée et mode non bloquant à budget CPU ; à justifier face à `gnutls` et `s2n-tls` déjà portés. | SDP : oui | Effort : moyen | Démo : session TLS sans bloquer la boucle critique | PR amont : support de cible | Originalité : 2

## Lot F — Applications temps réel médicales et automobiles (besoins normés)

1. **Vigie** — Robotics & Medical | IEC 60601-1-8 | Arbitre de tempête d'alarmes : priorités, escalade, acquittement, anti-noyade sonore, exposé comme gestionnaire de ressources. | QNX : resmgr + pulses prioritaires + `SCHED_SPORADIC` pour garantir la sonnerie | SDP : oui (logique portable) | Effort : moyen | Démo : 6 moniteurs, 40 alarmes en 10 s, la vitale passe devant | Originalité : 4
2. **Débit** — Robotics & Medical | IEC 60601-2-24 | Contrôleur de pompe à perfusion : boucle de débit déterministe, détection d'occlusion et de bulle d'air, état sûr. | QNX : `TimerPulse`, HAM, pulses d'alarme | SDP : partiel | Effort : moyen | Démo : occlusion injectée, arrêt avant surpression | Originalité : 3
3. **Souffle** — Robotics & Medical | IEC 80601-2-12 | Respirateur découpé en processus isolés où la panne d'un bloc ne coupe jamais la ventilation. | QNX : ASID, secpol, HAM | SDP : partiel | Effort : moyen | Démo : UI tuée, ventilation intacte | Originalité : 3
4. **Coffre** — Robotics & Medical | cybersécurité FDA premarket | Durcissement d'un dispositif médical : politique générée puis vérifiée, journal d'audit infalsifiable, attestation au démarrage. | QNX : secpol, abilities, Pathtrust | SDP : oui | Effort : moyen | Démo : trois attaques bloquées et tracées | Originalité : 4
5. **Banc** — Robotics & Medical | IEC 62304, validation | Simulateur de patient et injecteur de fautes côté hôte pilotant le dispositif QNX, verdict par exigence. | QNX : io-sock, PPS | SDP : oui | Effort : faible | Démo : scénario « désaturation », exigences cochées | Originalité : 4
6. **Chronique** — Robotics & Medical | dossier peropératoire | Timeline horodatée au tick noyau (alarmes, paramètres, injections, annotations) sans ralentir les dispositifs. | QNX : MsgReceive passif, horloge monotone, PPS | SDP : oui | Effort : moyen | Démo : intervention simulée, timeline exacte | Originalité : 3
7. **Double** — Robotics & Medical | IEC 62304, architecture deux canaux | Canal performant plus canal de sécurité indépendant dans un autre ASID, comparateur et état sûr. | QNX : ASID, secpol, SCHED_SPORADIC | SDP : partiel | Effort : moyen | Démo : divergence détectée, canal sûr prend la main | Originalité : 3
8. **Renouvellement** — Robotics & Medical | mise à jour d'un dispositif en service | Mise à jour transactionnelle d'un dispositif médical avec validation, retour arrière et journal pour l'auditeur. | QNX : image A/B, secpol | SDP : partiel | Effort : élevé | Démo : mauvaise version refusée, dispositif intact | Originalité : 4
9. **Garagiste** — Automotive & Mobility | ISO 14229 UDS + ISO 13400 DoIP | Serveur de diagnostic embarqué : sessions, accès sécurisé seed & key, DTC avec instantanés, routines, réponses à fenêtre garantie. | QNX : resmgr, io-sock | SDP : oui (pile protocolaire portable) | Effort : moyen | Démo : client `python-udsoncan` lit un DTC | Originalité : 4
10. **Horloge** — Automotive & Mobility | IEEE 802.1AS gPTP | Démon de synchronisation gPTP sur io-sock avec servo et mesure d'écart, pour fonctions réparties déterministes. | QNX : io-sock, horodatage, TimerPulse | SDP : non | Effort : élevé | Démo : écart entre deux nœuds sous la microseconde | Originalité : 4
11. **Borne** — Automotive & Mobility | ISO 15118 Plug & Charge | Contrôleur de borne : session 15118, PKI embarquée, bridage de puissance selon la capacité du bâtiment. | QNX : qcrypto, resmgr | SDP : partiel | Effort : élevé | Démo : session complète simulée, puissance bridée | Originalité : 3
12. **Cadran** — Automotive & Mobility | tableau de bord 60 Hz | Cluster à échéance stricte qui isole une application tierce plantée et se replie sur un affichage minimal. | QNX : secpol, HAM, Screen | SDP : partiel | Effort : moyen | Démo : appli tierce tuée, compteur toujours à 60 Hz | Originalité : 3
13. **Garde-fou** — Automotive & Mobility | ISO 26262, dégradation gracieuse | Superviseur de dégradation des fonctions ADAS : niveaux de repli, budget temporel, journal de transition. | QNX : HAM, pulses, SCHED_SPORADIC | SDP : oui | Effort : moyen | Démo : capteur perdu, repli de niveau 2 en 5 ms | Originalité : 4
14. **Trame** — Automotive & Mobility | CAN / SOME-IP | Passerelle CAN↔SOME/IP avec table de signaux (DBC/FIBEX) et pare-feu de messages : filtrage, cadence, anomalies. | QNX : resmgr, io-sock | SDP : oui | Effort : moyen | Démo : trame hostile filtrée, bus sain préservé | Originalité : 4
15. **Arène** — Automotive & Mobility | banc HIL logiciel | Banc matériel-en-boucle purement logiciel : bus virtuels, modèles de véhicule, injection de fautes, verdict par exigence. | QNX : QEMU, resmgr virtuels | SDP : oui | Effort : moyen | Démo : scénario de freinage rejoué à l'identique | Originalité : 3
16. **Piste** — Automotive & Mobility | UNECE R155/R156 | Journal de cybersécurité véhicule et traçabilité de campagne, exportable pour l'homologation. | QNX : slog2, secpol, abilities | SDP : oui | Effort : moyen | Démo : dossier d'homologation généré en une commande | Originalité : 3

---

# LES 7 RETENUS (classement par solidité de preuve, pas par enthousiasme)

Critères : trou vérifié dans la doc ou absence vérifiée dans l'index officiel des ports ;
réalisable en 5 semaines ; démontrable SANS le SDP (contrainte actuelle) ; catégorie encore
libre dans le portefeuille du candidat (il a déjà Automotive x2 et Tooling x1).

1. **Tamis** (= « Oracle » du lot A3, renommé : Oracle est une marque tierce, interdite en vidéo)
   — Developer Tooling — trous 1, 3, 10, 13 de la sécurité.
   Analyse statique AVANT déploiement : graphe types/abilities, chemins transitifs de
   délégation, règles sur-permissives, preuve de non-interférence, vérification du typage
   complet. Cœur C11 pur sur PC → **seul projet démontrable intégralement sans le SDP**.
   Vise le bonus « Best use of QNX-specific Technologies » (politiques de sécurité citées).
   Risque : un juge peut objecter que `secpolgenerate --diff` couvre une partie → répondre
   « la doc dit elle-même qu'il n'y a aucune analyse pré-exécution ».

2. **Échéancier** — Developer Tooling — trou 3 de l'outillage (originalité 5).
   Le développeur déclare période et budget ; l'outil vérifie chaque cycle sur la trace et
   nomme le responsable de chaque échéance manquée. Rien d'équivalent : `lmbench` mesure,
   il ne vérifie pas des échéances déclarées. Rend mesurables les promesses de `relais`.

3. **Éclat** — Open-Source Ports — absence VÉRIFIÉE par moi sur l'index officiel.
   WAMR (bytecodealliance/wamr) + courtier de capacités. Aucun port wasm/wamr/wasi/wasmtime
   dans `build-files/ports`, `qnx-ports/wamr` en 404. Cœur compilable sur PC, PR amont
   obligatoire et crédible. C'est l'idée la mieux documentée du lot.

4. **Écoute** — Open-Source Ports — absence vérifiée.
   Les trois shims noyau manquants regroupés en UN produit cohérent : `inotify`, `timerfd`,
   `signalfd`. Seul `epoll` existe et sert de modèle officiel. Débloque des milliers de
   projets POSIX ; PR amont vers tokio/mio/libev. Faible risque, forte visibilité.

5. **Vigie** — Robotics & Medical — IEC 60601-1-8 (catégorie vide dans son portefeuille).
   Arbitre de tempête d'alarmes en gestionnaire de ressources : pulses prioritaires,
   escalade, acquittement, `SCHED_SPORADIC` pour garantir la sonnerie sous charge.
   Meilleure démo des 100 (sonore et visuelle). Logique portable → testable sur PC.

6. **Banc** — Robotics & Medical — IEC 62304, effort faible.
   Simulateur de patient + injecteur de fautes côté hôte qui pilote le dispositif QNX et
   rend un verdict par exigence. Effort le plus faible des 7, et il sert de banc de test
   à Vigie → synergie immédiate entre deux soumissions.

7. **Veine** — Low-level Software — vsock absent des 20 vdev livrés (liste vérifiée).
   Canal hôte-invité fiable sans pile réseau. **Le plus risqué des 7** : exige le SDP et
   probablement le DDK hyperviseur, dont l'accès sous licence non commerciale n'est pas
   vérifié. À ne lancer qu'après installation du SDP.

## Arbitrages assumés

- **Trois projets en Developer Tooling** (Tamis, Échéancier + Passerelle déjà soumis) : ils
  se concurrencent entre eux. Si tu préfères élargir, remplace Échéancier par **Onde**
  (virtio-snd, Low-level) ou par **Étiquette** (mémoire partagée inter-OS typée et vérifiée).
- **Écartés malgré une originalité à 5** : **Toile** (virtio-gpu, le filon le plus cité) et
  **Réplique** (rejeu déterministe de trace) — tous deux exigent la cible et sont hors
  budget 5 semaines sans le SDP.
- **Écartés pour collision avec l'existant** : tout ce qui ressemble à `lmbench`/`sysbench`
  (déjà portés), à `secpolmonitor`/`libsecpolev` (fournis), à un transport virtio de
  système de fichiers (Passerelle), à un journal anticoupure (Ambre), à une bascule entre
  machines (Relais).

## Noms à corriger avant tout dépôt

Le lot A (sous-agent) a produit des collisions : **Jauge** et **Sillage** sont déjà des
dépôts de Baptiste ; **Navette**, **Miroir**, **Filtre**, **Contrôleur**, **Empreinte**
sont réutilisés ailleurs dans ce fichier. **Oracle** est une marque tierce (le règlement
interdit les marques de tiers dans la vidéo). Renommer : Oracle → Tamis, Jauge → Plages,
Sillage → Homologation, Empreinte → Stabilisateur, Miroir → Autocontrôle.

---

# RECLASSEMENT À 3 MOIS (~13 semaines) — v4

Le calibre change tout : la licence QNX Everywhere s'obtient en ~1 h, donc « exige le SDP »
n'est plus éliminatoire, et « effort élevé » devient réaliste. On privilégie alors la
profondeur et l'impact plutôt que la démontrabilité immédiate sur PC.

**CONFLIT DE CALENDRIER** : 3 mois depuis le 11/11/2026 = ~11/02/2027, soit APRÈS la
clôture du concours (15/12/2026 14 h ET) et après l'ouverture des délibérations (15/01/2027).
Un projet calibré 3 mois ne peut être soumis à ce concours que sous forme de sous-ensemble
livrable au 15/12. Les deux classements (5 semaines et 3 mois) sont donc conservés.

## Les 7 à 3 mois

1. **Toile** — Low-level — virtio-gpu. Trou le plus cité de tout l'inventaire (« aucune
   virtualisation GPU, Screen inutilisable en invité sans passthrough »). Originalité 5.
   Démo : un bureau QNX complet dans une VM. Risque : accès au DDK hyperviseur sous
   licence non commerciale, non vérifié.
2. **Éclat** — Open-Source Ports — WAMR + courtier de capacités. Absence vérifiée dans
   l'index officiel et `qnx-ports/wamr` en 404. Originalité 5. PR amont obligatoire.
3. **Réplique** — Developer Tooling — fusion de **Déclic** (figer la trace au crash) +
   **Réplique** (rejeu déterministe) + **Autopsie** (chaîne de blocage) : une machine à
   remonter le temps pour QNX. Deux notes d'originalité 5 sur trois. Impossible en 5 semaines,
   crédible en 3 mois.
4. **Tamis** — Developer Tooling — fusion d'**Oracle** (analyse statique pré-déploiement,
   o5) + **Grimpeur** (graphe d'élévation de privilèges, o5) + **Éplucheur** (purge des
   règles mortes) : un produit cohérent au lieu de trois utilitaires. Quatre trous documentés.
5. **Mouleur** — Low-level — trou 15 : « objets typés limités aux canaux ». Étendre le
   modèle de types et d'abilities aux mémoires partagées et aux connexions. Contribution
   profonde au modèle de sécurité QNX, pas un outil de plus.
6. **Vigie** — Robotics & Medical — arbitre de tempête d'alarmes IEC 60601-1-8, fusionné
   avec **Banc** (simulateur de patient + injecteur de fautes) pour produire un verdict de
   conformité par exigence. Catégorie vide dans le portefeuille.
7. **Doublure** — Automotive & Mobility — fusion de **Doublure** (A/B transactionnel avec
   rollback) + **Sceau**/**Scellé** (signature, démarrage vérifié) + **Crible** (conformité
   avant flash). Trou net : `mkqnximage --update` est une copie réseau sans atomicité,
   sans A/B, sans rollback. Marché UNECE R156. Réutilise le savoir-faire de journalisation
   atomique d'Ambre — mais concurrence Ambre et Relais dans la même catégorie.

## Devenus viables uniquement grâce aux 3 mois

Toile, Onde, Ballon, Veine (les 4 vdev absents) ; Réplique, Autopsie, Flamme (profilage
par échantillonnage) ; Mouleur, Miroir (auto-hébergement de la surveillance) ; Doublure,
Sceau, Scellé, Partition ; Horloge (gPTP 802.1AS), Borne (ISO 15118), Renouvellement ;
Bobine (FFmpeg), Pipeline (GStreamer), Compositeur (Wayland complet) ; Quic, Cadence (TSN).

## Inchangés par le calibre (déjà optimaux en 5 semaines)

Tamis, Échéancier, Éclat, Écoute (+ Tempo + Signe), Vigie, Banc : cœur portable, trou
vérifié, démonstration possible sur PC. Ce sont eux qui constituent le sous-ensemble
livrable au 15/12 si tu tiens à ce concours.
