# Inventaire officiel QNX SDP 8.0 — ce qui existe déjà (filtre anti-doublon)

Généré le 2026-11-11 par 6 sous-agents à partir de www.qnx.com/developers/docs/8.0, oss.qnx.com et gitlab.com/qnx.


## utilitaires

(lot absent)


## construction-image

J'ai tout ce qu'il faut. Voici l'inventaire.

## Outillage officiel QNX SDP 8.0 — image, amorçage, systèmes de fichiers

**Construction d'image**
- `mkqnximage` — génère une image système complète (VMware/VirtualBox/QEMU/QVM hypervisor + Raspberry Pi + cibles physiques) : partitions boot/system/data, personnalisation par « snippets » (ifs_files, system_files, ifs_start, slm, passwd…), `--run/--stop/--getip` (source: utilities/m/mkqnximage.html)
- `mkifs` — construit l'image OS « IFS » (.ifs) depuis un buildfile : startup, procnto, pilotes, libs ; montée en `/proc/boot` au boot (source: os_images/image_build.html)
- Buildfile d'image — 3 sections : `[bootstrap]` (arch + startup + noyau), `[+script]` (commandes exécutées par procnto au démarrage), fichiers inclus avec permissions/symlinks/compression (source: buildfiles/buildfile.html)
- `dumpifs` — liste le contenu d'une image .ifs (offsets, tailles, checksums) (source: os_images/image_build.html)
- `make` du BSP — le Makefile fourni construit IPL + IFS dans `/images` (chemin de recherche : install → `$QNX_TARGET`) (source: bsp/bsp_build.html)
- `diskimage` — crée une image de média partitionné contenant plusieurs filesystems (source: os_images/image_build.html)
- `mki` — préfixe une image d'un en-tête U-Boot ; `mkrec` — convertit un binaire en format ROM (source: utilities, liste M)
- `mkimage` — assemble une image « socket » à partir de fichiers individuels (source: utilities, liste M)

**Amorçage / démarrage**
- IPL (`ipl-*`) — chargeur 1er étage spécifique carte/arch (x86 board-agnostic, ARM board-specific) : init mini, trouve et valide l'IFS, le charge, saute vers startup ; + IPL Library pour en écrire un (source: ipl/ipl_about.html)
- `startup-*` — 1er programme de l'image : configure timers/IRQ/caches, remplit la system page, lance le noyau ; + Startup Library et Kernel Callouts (source: intro/intro_startup_sequence.html)
- `procnto-smp-instr` — noyau + process manager fusionnés ; exécute le `[+script]` du buildfile (source: os_images/images_about.html)
- SLM (System Launch and Monitor) — lancement ordonné d'applications multi-processus, sans toucher au buildfile (source: intro/intro_startup_sequence.html)
- QPLMS — service 8.0 de lancement/surveillance de processus piloté par dépendances (source: guides.html, nav OS Components)
- Boot Optimization Guide — techniques de réduction du temps de boot (early audio, HMI < 10 s), mesure de baseline, optimisation Screen (source: fastboot/fb_about.html)

**Systèmes de fichiers**
- `mkqnx6fs` / `mkqnx6fsimg` — formate / construit une image Power-Safe (fs-qnx6, crash-resilient, RW) (source: image_build.html, liste M)
- `mkefs` — image de flash filesystem embarqué (.efs, ETFS, NOR/NAND, RO ou RW/reclaim) (source: os_images/images_about.html)
- `mkfatfsimg` / `mkdosfs` — image FAT (host) / formatage FAT-12/16/32 (target) (source: liste M)
- `mksquashfsimg` — image SquashFS compressée lecture seule (source: liste M)
- `mkqfs`, `mkxfs`, `mount_ifs` — construction générique de FS QNX, montage d'un IFS (source: liste M)
- QFS (QNX Filesystem for Safety) — FS lecture seule à protection d'intégrité (expérimental) (source: guides.html, nav)
- `devb-*` — pilotes bloc (sdmmc, eide…) démarrés depuis le script de boot ; création de FS sur cible documentée (source: images_about.html, filesystem_create.html)
- **Absents de la réf 8.0** : `mkdinit` et `mkrecfs` (existants en 7.1) ne figurent plus dans la liste des utilitaires M (source: utilities-m.html)

**Mise à jour, sécurité d'image**
- `mkqnximage --copy[=b|s|d|all]` — écriture image/partitions sur carte SD (règles udev pour les permissions) (source: mkqnximage.html)
- `mkqnximage --update` — mise à jour « OTA » : copie des partitions par le réseau puis relance des devb-* ; ne sait pas redimensionner les partitions (source: mkqnximage.html)
- Security policies + `secpolgenerate` — abilities centralisées injectées dans l'image au build ; Pathtrust et fonctions fortifiées côté runtime (source: security.system/manual/about.html)
- `mkqnximage` embarque un mode démo des fonctionnalités de sécurité (source: security mkqnximage_security.html)

## Conclusion — ce que QNX ne fournit PAS (trous exploitables)

1. **Pas de chaîne de signature/vérification d'image générique** dans le SDP : checksums visibles via `dumpifs` seulement ; le secure boot dépend du bootloader/carte — un outil de signature+vérification portable est un vrai trou.
2. **Pas d'OTA robuste** : `--update` = simple copie réseau sans atomicité, ni A/B, ni rollback, ni gestion de version — un update manager transactionnel avec fallback est inédit.
3. **Pas d'outil unifié multi-cibles** : `mkqnximage` couvre VM + Raspberry Pi, les autres cartes passent par `make` manuel dans le BSP ; rien pour orchestrer/visualiser/différencier des images multi-cartes (CI-friendly).
4. **Pas d'instrumentation clé en main du temps de boot** : le guide d'optimisation est méthodologique, sans dashboard automatisé de mesure par phase (IPL/startup/script/app).
5. **Pas d'assistant de buildfile ni d'équivalent mkdinit/mkrecfs en 8.0** : l'édition reste textuelle et experte — générateur/valideur interactif de buildfile = espace libre.

Note : quelques fetchs ont rendu des 403 transitoires (proxy), résolus en réessayant les URLs canoniques ; aucune page inaccessible au final sur le périmètre couvert.


## architecture-noyau

(lot absent)


## securite

Toutes les 21 pages ont été lues avec succès (aucune inaccessible). Voici la synthèse.

# Inventaire sécurité QNX SDP 8.0 (System Security Guide)

## A — Ce que la chaîne officielle fournit déjà

**Abilities (noyau/procnto)**
- ~70 abilities **statiques** (procmgr) : chaque processus a 2 jeux (root/non-root) ; sous-plages numériques possibles ; secpolcompile fusionne les sous-plages contiguës (source: abilities.html, abilities_reference.html).
- Liste complète avec ce que chacune autorise : able_create, able_priv, channel_connect, child_newapp, chroot, clockset, confset, connection, cpumode, default_timer_tolerance, event, fork, getid, high_resolution_timer, hyp, interrupt, io, mac_policy, map_fixed, mem_add/lock/peer/phys/special, mountifs, msg_queue, pathspace, path_trust, pgrp, power, priority, privreg, prot_exec, prot_write_and_exec, public_channel, reboot, rlimit(_peer), rsrcdbmgr, runstate, schedule, server_monitor, session, setgid, settypeid, setuid, sigev_thread, signal, spawn(_setgid/_setuid), srandom, swap, trace, umask, untrusted_exec, wait, xprocess_able/debug/mem_read/query (source: abilities_reference.html).
- **Custom abilities** (dynamiques, par nom) : fsevmgr/*, iofunc/chown|dup|exec|read, io-gpio/all, network/privport|rawsocket|reuseport|ipsec|admin|jailroot, smmu/*, vfs/* (source: abilities_reference.html).

**Langage de politique (secpol.txt → secpolcompile → secpol.bin → secpolpush)**
- Éléments : `type`, `attribute` (groupes de types), `class` (permissions custom), `range` (plages nommées résolues au boot via fichier `ability:range_name:syspage:/…`), `default_rules` (source: secpol_language.html, named_range_file.html).
- Règles : `allow src dst:ability{…}` (avec plages, `nonroot`, `unlock`, `noinherit`, `gain_priv`), `allow src dst:channel connect`, `allow_attach type chemin [ftype:] [type_canal]` (wildcards `*` et `...`), `allow_link`, `default_spawn_type`, `derive_type`, `mount_point uid:gid perms/ACL chemins` (source: secpol_language.html).
- Compilateur : détecte types non déclarés, erreurs gain_priv (avertissements/erreurs si privilèges acquis par settypeid non déclarés), fusion de sous-plages (source: secpol_language.html, using_security_policy_types.html).
- Types applicables aux processus (on -T, slm, posix_spawn) ; **seul objet typable natif = le canal** ; classes custom pour tout autre objet, à coder côté resource manager avec `secpol_get_permission()`/`secpol_check_permission()` (source: using_security_policy_types.html, secpol_language.html).

**secpolgenerate (génération par observation)**
- Tourne sur la cible, observe les tests d'abilities/chemins via le trace noyau, produit `/dev/secpolgenerate/policy` (texte), `/errors` (règles manquantes + sigevents non enregistrés, ≤10/processus), `/unused` (règles jamais utilisées) ; options -u (illimité), -t N types, -c fichier config (types `unrestricted`), -s/-n (état persistant), -r (plages nommées), -C load (injection de **fichiers d'événements** compilés avec `secpolcompile -e` pour simuler des usages rares), -v (erreurs sur stderr) (source: using_security_policies.html, debugging.html, event_files.html, tuning.html).
- Modes : génération initiale, **diff incrémental** contre politique existante, et **monitoring en système déployé sécurisé** (règles minimales documentées pour secpolgen_t/secpolmonitor_t) (source: tuning.html, using_secpolgenerate_secure_system.html).
- Aussi : secpolmonitor (sortie temps réel), secpolpush (applique, seul à résoudre les plages nommées), secpol (visualisation), secpol-preload.so, secpollaunch (spawn avec transition de type en root, évite gain_priv) (source: security_policies.html, secpol_language.html, named_range_file.html).

**APIs**
- `libsecpol` : baisser ses privilèges après init, spawner avec privilèges réduits, permission fine custom, traduction nom↔ID de type ; fonctions secpol_open/close/check_permission/get_permission/get_type_id/get_type_name/get_policy_id/resolve_name/transition_type/type_id/posix_spawnattr_settypeid/resmgr_attach, get/set_ids_from_arg ; marche avec ou sans politique (source: libsecpol_api.html).
- `libsecpolev` : consommation des événements de trace politique — secpolev_init/wait_event/shutdown/flush, get_process_name/type/pid/timestamp, get_ability_info/path_info/custom_perm_info, get_dropped_count, callback de log ; événements ABILITY_TEST, PATH_ATTACH, PATH_LINK, CUSTOM_PERM avec flag DENIED (source: libsecpolev_api.html, secpol_event_monitor.html).

**Pathtrust** : empêche l'exécution de code non fiable (binaires + dlopen) ; ignore setuid/setgid sur FS non fiable ; exige procnto -qt, ability path_trust pour devb/mount -o trusted, partition à intégrité (QTD) ; mkqnximage --pathtrust pour démo (source: pathtrust.html).
**Fonctions fortifiées** : `_FORTIFY_SOURCE=1|2`, ~170 fonctions libc/Msg*/resmgr_* avec variantes `__*_chk`, validation compile+runtime, termine le processus en cas d'anomalie, surcoût négligeable (recommandé en production) ; qchecksec vérifie le niveau (source: fortified.html).
**mkqnximage** : images démo --procfs sécurisé, --pathtrust, QTD, secpol ; méthode = diff des fichiers output/build entre deux images (source: mkqnximage_security.html).
**Security matrix** (couverture déjà revendiquée) : confidentialité au repos (chiffrement FS), intégrité/signature (QTD, secure boot), accès RM (politiques, ACL), exécution non fiable (pathtrust), détournement de contrôle (RELRO), ASLR, débordements buffer/pile (fortified, canaries), fuite d'info (/proc sécurisé), moindre privilège (politiques+abilities+ACL), DMA (SMMUMAN), DoS (rlimit, jails réseau), MITM/snooping réseau (jails) (source: security_matrix.html).

## B — Trous reconnus par la doc (sourcés)

1. **Revue des règles inutiles = manuelle** : « QNX recommends that you review the security policy specifically to locate processes with abilities that they don't need » ; /unused n'est qu'« a guide » car « it is possible that they're only required under circumstances that have not yet occured » (review_policies.html, security_policy_maintenance.html). Aucun outil ne tranche.
2. **Politique générée non utilisable telle quelle** : « The secpolgenerate utility is not designed to generate a security policy that you can use as is. Rather, it is intended to provide input into a policy that you modify » ; simplification (wildcards, attributes) à refaire à la main (security_policy_maintenance.html).
3. **Aucune analyse statique/pré-exécution** : la politique ne couvre que « behavior that secpolgenerate observed when you exercised the system » ; il faut « continue to exercise your system … so that secpolgenerate can more thoroughly track all the possible activity » — pas de preuve de couverture avant déploiement (using_security_policies.html).
4. **Échecs invisibles à l'outil** : « There are ways in which a system can fail that are invisible to secpolgenerate and thus won't show up in its errors file » (ex. permissions de fichiers, root→non-root) ; solution proposée : « identify the paths that it fails to open »… manuellement (troubleshooting.html).
5. **Faux positifs non résolus** : erreurs setuid/setgid/prot_exec/priority sans échec réel ; « Some of these might be partially resolved by secpolgenerate, others might require procnto changes » ; setuid() « not possible to fix … required for proper POSIX behavior » (troubleshooting.html).
6. **Instabilité entre exécutions** : « each time you run a system, secpolgenerate generates new rules that define new subranges » ; parade = retirer les sous-plages à la main et « grant the ability in an unrestricted manner » — pas d'outil de diff/stabilisation de politique entre versions (troubleshooting.html).
7. **default_spawn_type jamais généré** : « You have to add the default_spawn_type keyword manually. Because secpolgenerate has no way to determine if a process should change its type, it never adds a default_spawn_type rule » (secpol_language.html).
8. **Analyse d'élévation de privilèges artisanale** : pour savoir quel type apporte quel privilège, « comment out gain_priv in the policy and compile it. The error messages indicate the type » — essai/erreur, pas d'analyse de non-interférence entre types (secpol_language.html).
9. **Fusion des nouvelles règles = manuelle** : « these additional rules are merged with existing rules rather than concatenated » ; le choix des règles à garder (« you would probably ignore rules for console_t ») est laissé à l'humain (security_policy_maintenance.html, tuning.html).
10. **Vérification du typage complet = manuelle** : « run pidin -f a_n after startup and check the output to make sure that all processes have a security type » ; l'unicité de type par service n'est qu'un « CAUTION », non vérifié par outil (using_security_policy_types.html, using_security_policies.html).
11. **libsecpolev verrouillé et non auto-découvert** : « can only be used by one program at a time, and you can't use it at the same time as tracelogger » ; l'ability trace requise « can't [be] discover[ed] … by secpolgenerate and secpolmonitor, you have to manually give it » (secpol_event_monitor.html).
12. **Boucle de dev lourde** : modifier le fichier config de secpolgenerate impose « you have to rebuild the IFS each time » ; la parade documentée est un montage manuel en 5 étapes (tuning.html).
13. **Plages nommées fragiles, non validables à froid** : « If any range can't be resolved … the policy is not pushed and it is likely the system won't boot » ; secpolpush ne fusionne pas les plages adjacentes (named_range_file.html).
14. **secpolgenerate ne peut pas s'auto-héberger** : « it can't monitor its own usage until it starts, and after it has started it is too late » — ses propres règles sont à écrire à la main (using_secpolgenerate_secure_system.html).
15. **Objets typés limités aux canaux** : « Currently, the only object that QNX OS provides that can be given a type is a channel » ; tout objet métier exige une classe custom **codée** dans le RM, sans audit que le check est bien fait (using_security_policy_types.html).

## C — Conclusion (projets de concours recevables)

1. La génération par observation existe (secpolgenerate), mais **tout l'aval est manuel** : revue, simplification, fusion, stabilisation — c'est le cœur des opportunités.
2. Projet fort : **« policy diff/linter »** — comparaison sémantique de politiques entre versions (sous-plages, types, attributes), détection d'élargissements de privilèges, fusion automatique de règles diff ; les trous 2, 6, 9 le justifient texte à l'appui.
3. Projet fort : **analyse statique/épreuve de couverture** — combiner fichiers d'événements (`secpolcompile -e`), `/unused` et `/errors` pour prouver qu'une politique couvre les scénarios rares **avant** déploiement (trous 1, 3, 4).
4. Projet recevable : **assistant gain_priv/default_spawn_type** — inférer les transitions de type et les élévations à partir du code (appels secpol_transition_type) et du graphe settypeid, là où la doc prescrit l'essai/erreur (trous 7, 8).
5. À éviter : réinventer la génération d'abilities, le monitoring brut (libsecpolev/secpolmonitor existent) ou une « matrice attaque/mitigation » (security_matrix la fournit déjà).


## hyperviseur-conteneurs-reseau-screen

Inventaire terminé — toutes les pages cibles ont été atteintes (quelques 403 proxy transitoires, résolus au retry ; aucun échec définitif).

# QNX SDP 8.0 — ce qui est déjà fourni

## 1. Hyperviseur (QNX Hypervisor 8.0.4 / Hypervisor for Safety)
- Micro-noyau + virtualisation intégrée au kernel, VM créées par processus `qvm` — architecture Popek/Goldberg, 64 bits seulement (AArch64/ARMv8, x86-64) (source: virt/virt.html, virt/support.html)
- **Invités supportés** — QNX OS for Safety 8.0.4 (variante QHS), QNX OS 8.0+, Linux Ubuntu 22.04 ; Android/autres = via QNX Engineering Services ; 32 bits abandonné (source: virt/support.html)
- **Configuration invité** — un processus `qvm` par VM, config par ligne de commande ou fichiers `guest.qvmconf` (typiquement `/guests/qnx80/qnx80-guest1.qvmconf`), lecture en une passe, tables ACPI + FDT exposées aux invités (source: config/qvm.html, config/acpi_fdt.html)
- **Sécurité/isolation** — niveaux de privilège CPU (invité < kernel), stratégies de protection, « design safe states », confinement DMA via IOMMU/SMMU manager, watchdogs virtuels, notification de terminaison `qvm`, détection d'environnement virtualisé (source: protection/protection.html et sous-pages)

### Liste exhaustive des vdev livrés (20) — (source: vdev_ref/vdev_ref.html)
- `8259` — émulation minimale Intel 8259 PIC (x86)
- `gic` — émulation ARM Generic Interrupt Controller
- `hpet` — fournit un HPET à l'invité
- `ioapic` — émulation Intel IOAPIC
- `mc146818` — émulation horloge temps réel Motorola 146818
- `pci-dummy` — périphérique PCI inactif, lecture seule
- `pci-host-bridge` — pont hôte PCI
- `pckeyboard` — contrôleur clavier IBM PC (seul « HID », legacy x86)
- `pl011` — série ARM PL011
- `progress` — trace des accès mémoire/instructions de l'invité (debug)
- `ser8250` — émulation UART Intel 8250 (série/console)
- `shmem` — mémoire partagée inter-OS
- `smmu` — sous-ensemble smmu-*.so pour smmuman dans un invité QNX
- `timer8254` — émulation timer Intel 8254
- `virtio-blk` — bloc standard VIRTIO
- `virtio-console` — console standard VIRTIO
- `virtio-entropy` — RNG/entropie pour l'invité
- `virtio-net` — réseau standard VIRTIO
- `wdt-ib700` — watchdog IB700
- `wdt-sp805` — watchdog ARM SP805

**Non fournis** : virtio-gpu, virtio-snd (son), vsock, virtio-balloon, virtio-input moderne, virtio-scsi, virtio-fs, USB virtuel, virtio-crypto. API + guide développeur vdev publics (`vdev-*.so`, GitLab qnx/hypervisor) pour en écrire (source: vdev_ref/vdev_ref.html, hypervisor.nav/bookset.html).

## 2. Conteneurs (QNX Containers 1.0)
- `qrunc` — runtime bas niveau conforme OCI : isolation FS + CPU/mémoire, lancement/surveillance des processus, logs, exec/attach, nettoyage (source: containers/overview.html)
- `qcmgr` — runtime haut niveau : messages de contrôle, gestion d'images (registry ou tar), réseau par configuration de pod, orchestre qrunc ; notion de **pod** façon Kubernetes (source: containers/overview.html, about.html)
- `qcmctl` — CLI client de qcmgr (source: containers/appendix_qcmctl.html)
- Isolation réseau par « Network Jail » ; politiques de sécurité documentées (source: containers/appendix.html)
- **Limites** — pas de namespace de processus (pidin voit tout l'hôte), applis privilégiées non contenues (root dans le conteneur peut éteindre l'hôte), setuid neutralisé, bug connu de perte du network jail sur fork/exec, restart = tuer qrunc+qcmgr (source: containers/appendix_caveats.html)

## 3. Réseau (io-sock, pile haute performance)
- `io-sock` — gestionnaire réseau en espace utilisateur, code/architecture alignés FreeBSD 14.4, TCP/UDP/IPv4/IPv6 intégrés, chiffrement + Wi-Fi intégrés, multi-instances possibles, drivers chargeables dynamiquement (source: io_sock/about.html, overview.html)
- **Protocoles livrés** — ICMP, ICMP6, IPsec, IPv4, IPv6, ROUTE, SCTP, TCP, UDP, Unix-domain (source: io_sock/protocols.html)
- **Services livrés** — CARP (redondance d'adresses), LAGG (agrégation), netmap (packet I/O rapide), TAP, TUN, VALE (switch virtuel via netmap), VLAN 802.1Q ; + BPF et PF/pfctl (filtrage, NAT) (source: io_sock/services.html, overview.html)
- **Extensibilité** — guides « Writing Network Drivers for io-sock » + driver exemple, « Writing an io-sock Module » + module minimal, PTP 2-step (timestamping Tx/Rx, API module PTP) (source: io_sock/about.html, sample_module.html, ptp_api.html)
- **io-pkt** — ancienne pile, officiellement *remplacée* par io-sock depuis SDP 7.1 ; doc de migration io-pkt→io-sock fournie (source: migration/networking.html, migrate_app.html)

## 4. Graphisme / Screen 4.0
- Screen — modèle client/serveur avec **composition fenêtrée** (rendu off-screen), buffers/pixmaps/windows/streams, partage de ressources inter-processus, multi-écrans + déplacement de curseur entre displays, entrées/événements/notifs asynchrones, API function-safety, config par `graphics.conf` (source: screen/cscreen_about.html)
- **Wayland on Screen** — implémentation C du protocole Wayland core (source: screen/cscreen_wayland.html)
- Écosystème : Screen DDK (pilotes GPU/display maison), OpenWF (wfd-server, Wfdcfg), lib Gestures, Input Events, Image Library, Video Capture, utilitaires calibration/debug (source: qnxsdp.nav/graphics.html)
- **Sécurité** — doubles politiques (init puis runtime) pour screen et DRM, transition manuelle `drop_privileges` via `/dev/screen/command` et `/dev/dri/qnxcommand`, GPU dropping privileges, ACL sur `/dev/dri/card0`/`renderD128`, abilities `channel_connect` pour clients non-root (source: screen/cscreen_security.html)

## Conclusion — candidats pour le hackathon (6 lignes)
1. **vdev manquants = meilleur filon « Low-level Software »** : virtio-gpu (aucune virtualisation GPU, Screen inutilisable en invité sans pass-through), virtio-snd (zéro son virtualisé), vsock (pas de canal socket host↔invité), virtio-balloon (mémoire statique), virtio-input moderne — l'API vdev est publique, documentée, avec samples et repo GitLab.
2. **Réseau** : pile complète (SCTP, PF, VLAN, netmap inclus) — ne pas refaire TCP/IP ; un **module io-sock** (API documentée) type QUIC, TSN/AVB, ou broker MQTT/DDS temps réel reste inédit ; io-pkt est mort, viser io-sock uniquement.
3. **Conteneurs** : pas de namespace PID, pas de confinement root, jail réseau bogué → outillage de supervision/isolation complémentaire possible, mais cœur déjà livré (qrunc/qcmgr/qcmctl, pods, registries).
4. **Screen** : composition, multi-écran, Wayland core déjà là ; candidats « Ports » : extensions Wayland/compositeur complet, streaming VNC/WebRTC de surfaces Screen, ou port d'applications Linux dans l'invité Ubuntu 22.04 (supporté officiellement par l'hyperviseur, Android non).


## ecosysteme-oss

## Inventaire open source QNX — hackathon 2026

**Sources consultées** : oss.qnx.com ✅ (SPA JS : compteurs visibles — **866 projets / 2 592 paquets / 13 931 builds** — mais aucune API JSON accessible, 3 endpoints tentés → 404 ; liste exhaustive non extractible), gitlab.com/qnx ✅ (via API GitLab), qnx.software/qnx-everywhere ✅, qnx.devpost.com/resources ✅, github.com/qnx ✅ et github.com/qnx-ports ✅ (via API GitHub + arbre du dépôt `build-files/ports`, ~120 ports).

### A. Ports open source maintenus par QNX (github.com/qnx-ports, liste = `build-files/ports/`)

**Compression** : zlib, zstd, lz4, brotli, bzip2 — tous https://github.com/qnx-ports/build-files/tree/main/ports/<nom>
**TLS/crypto/sécu** : gnutls, nettle, s2n-tls, strongswan (IPsec), sscep, libssh2
**BD** : sqlite, sqlite_orm
**Réseau** : curl, nghttp2, c-ares, libwebsockets, dnsmasq, unbound (DNS), tftp-hpa, lighttpd1.4, NTPsec, chrony, mosquitto (MQTT), libzmq (ZeroMQ), amqp-cpp, restbed
**Sérialisation/RPC** : protobuf, grpc, flatbuffers, capnproto, cJSON, jansson, libjson, rapidjson, libyaml, tinyxml2, pugixml, libxml2, libexpat, icu
**Robotique/auto** : ros2 (+ paquets vendor), Fast-DDS, Fast-CDR, vsomeip (SOME/IP), dlt-daemon (logs GENIVI), lely-core (CANopen), CANdb, open-amp + libmetal (AMP), **epoll (shim)**
**Cloud IoT** : aws-c-common/-cal/-io, aws-crt-cpp, azure-iot-sdk-c
**IA/math** : pytorch, tensorflow, onnx, onnxruntime, XNNPACK, ruy, ARM ComputeLibrary, OpenBLAS, eigen, ceres-solver, gtsam, SuiteSparse, METIS, clapack, sleef, cpuinfo, kineto
**Graphique/GUI/multimédia** : qt, gtk, wayland, weston, cairo, pixman, graphene, gdk-pixbuf, freetype, harfbuzz, fontconfig, graphite, fribidi, libthai, libdatrie, libxkbcommon, xkeyboard-config, nanosvg, FreeImage, libpng, libjpeg-turbo, libyuv, SDL, SDL_ttf, openal-soft, libsndfile, vlc, webrtc, pdfium, libcamera
**Langages/outils** : **rust**, **lua**, **perl5**, numpy, numpy2, pandas (donc toolchain Python présente), bash, vim, tree, minicom, picocom, glib, gettext-runtime, libffi, libiconv, libusb, libuv, libevent, libev, asio, pcre2, re2, gmp, mpfr, muslflt
**Test/bench/logs** : googletest, Catch2, benchmark, check, cunit, trompeloeil, csmith, sysbench, lmbench, glog, g3log, gflags, abseil-cpp, boost, oneTBB
**Démos/radio** : mame, RetroPie, rtl-sdr, dump1090

### B. Projets d'exemple officiels (gitlab.com/qnx)

**Capteurs/caméra** : `qnx/projects/camera-projects` — camera_example1_callback, example2_events, example3_viewfinder, example4_record, camera-list, camera-dump-frame(-no-screen), camera-manual-exposure, rpi4-debayer-example, rpi-isp-tuning-example ; pile RPi Camera : vchiq(+interface), vcsm(+interface), v_isp (MMAL), platform_broadcom (CSI2/ISP), rpi_mbox_interface, rpi5
**IA** : ai-camera-app (TFLite + QNX Sensor Framework), pytorch_classifier_example (PyTorch Mobile), ai-services-rest-examples (REST Gemini) — https://gitlab.com/qnx/projects ; QNX-AI-workshop — https://github.com/qnx/QNX-AI-workshop
**Matériel RPi** : rpi-gpio (resource manager GPIO + modules Python rpi_gpio/smbus), rpi-mailbox, rpi-thermal, trilobot (Pimoroni), rainbow-hat-qnx, usb-to-screen (gamepad HID→libscreen)
**Système/portage** : simple-terminal (terminal de l'image Quick Start), shim-demo (**shim eventfd**, modèle de portage), drivers/ure
**Robotique** : robot-arm + gamepad-control-with-ros2, qnx-ros2-workspace, ros2-multi-imu-demo (BNO055 multi-nœuds)
**Jeux/3D** : quake3e, sample-apps/vkcube (Vulkan)
**Hyperviseur** : hypervisor/getting-started (QHV multi-guests Pi 4B), fdt-examples, working-with-time, vdev-shmem (device mémoire partagée pour guest Linux), working-with-hardware, virtual-device-developers-guide
**Éducation** : ateliers traffic-lights, codelabs — https://qnx.github.io/codelabs
**Images/BSP** : quick-start-images (image RPi QNX 8.0 avec apps démo open source) ; BSP open source **github.com/qnx/bsp_raspberrypi-bcm2711-rpi4** et **…bcm2712-rpi5** ; QNX-Toolkit-for-VS-Code-Examples, qnx-agent-skills

### C. QNX Everywhere (gratuit, non commercial)
SDP 8.0 (noyau + toolchain + utilitaires debug/profilage dont outils open source), QNX Developer Desktop (auto-hébergé), QNX Hypervisor, formations gratuites (learning.qnx.com), image Quick Start RPi 5, toolkit VS Code ; « 2,5K ports open source » publiés sous licences d'origine ; guide **Linux Porting Guide** dédié à la catégorie du concours. Pas de liste détaillée des libs *dans* le SDP trouvée (doc derrière bookset), mais les ports ci-dessus couvrent l'écosystème.

### Conclusion (6 lignes)
1. **Pièges (déjà faits, à éviter)** : TLS/compression (gnutls, s2n, zlib/zstd/lz4/brotli), SQLite, protobuf/gRPC, OpenCV/ONNX Runtime/PyTorch/TensorFlow, Qt/GTK/Wayland/Weston/SDL, MQTT/ZMQ/DDS/ROS 2, curl/boost, Rust, Lua, Perl, numpy/pandas, epoll (shim) et eventfd (démo officielle).
2. **Manques crédibles en 4 semaines + PR amont** : **ffmpeg** ou **GStreamer** (multimédia : vlc/webrtc présents mais pas de framework de pipeline), **git** (bash/curl/ssh2/zlib déjà là — dépendances prêtes), **jq**, **htop/tmux**, petits outils CLI POSIX.
3. **Shims noyau à forte valeur** : inotify/timerfd/signalfd (sur le modèle du shim eventfd officiel) avec PR amont vers les consommateurs (tokio/mio, libev…) — très visible pour la catégorie Ports.
4. **Python** : numpy/pandas sont portés mais un CPython 3.x complet + pip est un gros morceau ; faisable seulement en reprise de l'existant qnx-ports.
5. **Go/Node.js** : ambitieux (runtime/V8) — plutôt hors budget 4 semaines, sauf contribution partielle amont.
6. Vérifier chaque candidat sur **oss.qnx.com** (866 projets, liste complète non scrapable) et dans `qnx-ports/build-files/ports/` avant de s'engager : c'est la source de vérité « déjà porté ou non ».

---

# CORRECTIF MAJEUR (11/11 20:25) — l'inventaire précédent était biaisé

L'inventaire initial n'a couvert que 5 chapitres et a conclu à des « absences » en ne
regardant que la référence des **utilitaires en ligne de commande**. Or QNX livre une
suite IDE complète (QNX Momentics, base Eclipse) que je n'avais pas ouverte.

## Ce que l'IDE Momentics fournit déjà (source : com.qnx.doc.ide.userguide/topic/about.html)

- **Debugging** : application en cours, bibliothèque, **et fichier core**.
- **Unit Testing** + outil de **couverture de code**.
- **Memory Analysis** + outils **Valgrind** (fuites, corruption) + perspective *QNX System
  Information* (processus consommant excessivement mémoire/ressources).
- **Analyzing Performance** : **Application Profiler** + **Valgrind Cachegrind**.
- **Analyzing System Behavior** : *QNX System Information* et *QNX System Profiler* pour
  « understand process and thread interaction on the target, **reduce application and
  system startup times**, and **debug deadlock** and improper CPU usage levels ».
- **Building QNX OS Images** : *QNX System Builder* (génération d'images amorçables,
  transfert vers la carte).
- **JTAG** : débogage matériel via Lauterbach TRACE32.

## Ce que le SAT fournit déjà (source : com.qnx.doc.sat/topic/datainterpretation.html)

Citation exacte : « The best tool (by far) for interpreting the copious amounts of trace
data is the QNX Momentics IDE. [...] We also provide a traceprinter utility that simply
prints a plain-text version [...] You can also **build your own custom interpreter, using
the traceparser library** ».
Donc : capture, filtrage, buffers noyau, interprétation et **bibliothèque traceparser**
existent. L'analyse de trace n'est PAS un trou.

## Ce que QFS fournit déjà (source : com.qnx.doc.neutrino.qtsafefs/topic/about.html)

QNX Filesystem for Safety : système de fichiers **lecture seule à protection d'intégrité**,
en deux versions (certifiée sous licence QOS 8.0 ; **expérimentale incluse dans le SDP 8.0**),
avec `mkqfs`, `qtsafefsd`, et appui sur la bibliothèque qcrypto.

## Conséquences : trous révoqués ou fortement affaiblis

- T1 « pas de profileur par échantillonnage » → **FAUX** : Application Profiler + Cachegrind.
- T2 « traceprinter brut, aucun agrégat » → **TROMPEUR** : l'IDE agrège, et `traceparser`
  est fourni pour écrire son propre analyseur.
- T4 « post-mortem non corrélé » → **PARTIELLEMENT FAUX** : le System Profiler aide
  explicitement à « debug deadlock », et l'IDE ouvre les fichiers core.
- T5 « supervision pauvre » → **AFFAIBLI** : perspective QNX System Information.
- I4 « boot non instrumenté » → **FAUX** : le System Profiler vise la réduction des temps
  de démarrage applicatif et système.
- I5 « pas d'assistant de buildfile » → **AFFAIBLI** : QNX System Builder génère des images.
- I1 « pas de signature d'image » → **AFFAIBLI** : QFS protège l'intégrité (lecture seule)
  et qcrypto fournit les primitives.

## Trous qui survivent à ce correctif

- S1/S2/S3/S8/S9/S10/S13/S15 (politiques de sécurité) : aucun outil d'analyse statique de
  politique trouvé, ni dans l'IDE ni ailleurs. **Tamis survit intact.**
- T3 (vérification d'échéances déclarées, en CI, sans IDE) : rien d'équivalent trouvé.
  **Échéancier survit**, à repositionner comme outil headless/CI au-dessus de `traceparser`.
- Rejeu déterministe d'une trace dans un modèle d'ordonnanceur : rien d'équivalent trouvé.
  **Réplique survit** amputée de sa partie « chaîne de blocage » (couverte par l'IDE).
- H1 virtio-gpu, H3 vsock : toujours absents des 20 vdev. **Toile et Veine survivent.**
- P1 WebAssembly : toujours absent de l'index officiel des ports. **Éclat survit.**
- I2 A/B + rollback + orchestration de campagne : toujours absent (`mkqnximage --update`
  reste une copie réseau). **Doublure survit** amputée de sa partie signature.

## Livres jamais lus = le vrai gisement inexploité

Device Publishers (RMPS, framework capteurs) · High Availability Framework (HAM) · QPLMS ·
**SMMUMAN** (SMMU, confinement DMA) · PCI Server · Building Embedded Systems · Customizing
a BSP · Boot Optimization · QFS · io-sock User's Guide · Technotes · Introspection API ·
QNX Software in the Cloud · QNX Developer Desktop · Toolkit VS Code · C Library Reference ·
Devctl/Ioctl · Migrating to 8.0 · Getting Started / Programmer's Guide / Writing a Resource
Manager · System Architecture.

---

# TROUS NOUVEAUX (11/11 20:30) — API C, migration 7.1→8.0, devctl, Introspection API

Source : sous-agent ayant lu com.qnx.doc.qnxsdp.migration, com.qnx.doc.neutrino.devctl,
com.qnx.doc.introspection, com.qnx.doc.neutrino.lib_ref. L = lu dans la doc, S = supposé.

## Résultat — 14 `web_fetch` tentés (10 lus, 4 en 403 : pages `API.html`/`kernel.html` de la Discontinuation Notice inaccessibles via le proxy)

**Lu** = confirmé dans la doc ; **Supposé** = inférence signalée.

### (A) Trous nouveaux (18)

| code | trou (L=lu, S=supposé) | source | exploitable pour le concours |
|---|---|---|---|
| LIBC-01 | `inotify_*` **n'a pas disparu** : déplacé de libc vers `libfsnotify.so` (L) — l'hypothèse du parent est fausse | migration/c_apps | couche de compat Linux→QNX + détecteur auto de linkage ; corrige une idée existante |
| LIBC-02 | `_smalloc/_scalloc/_srealloc/_sfree` supprimés de libc (L) | migration/c_apps | lib API-compatible + scanner de code legacy qui les utilise |
| LIBC-03 | `itoa/ltoa/lltoa/ultoa/ulltoa/utoa` supprimés de stdlib.h (L) | migration/c_apps | auto-patcheur vers `snprintf`, linter de portage massif |
| LIBC-04 | C++11/14 discontinués, libc++ seul, C++17/20 (L) | migration/c_apps | analyseur/statique de migration C++ legacy |
| MIG-01 | Binaires 7.1 **inexécutables** en 8.0, rebuild complet obligatoire (L) | migration/c_apps | estimateur d'effort de migration + orchestrateur de rebuild CI |
| DEVCTL-01 | Classe `DCMD_INPUT_*` **obsolète**, aucun remplacement documenté (L) | devctl/about | ressource manager + API d'entrée unifiée (HID/tactile) |
| DEVCTL-02 | `PART_*` (partitions) obsolète (L) | devctl/about | outillage de gestion de partitions moderne (CLI/GUI) |
| DEVCTL-03 | `DIOC*` (firewall PF), `TAP*/TUN*`, `GRES*`, `SRT*`, `SIOC*` : doc **renvoyée vers les man FreeBSD 14.4**, rien de natif (L) | devctl/about | suite de tests + doc + outils réseau spécifiques QNX sur ces ioctls |
| DEVCTL-04 | `SND_*`, `DCMD_MEDIA_*`, `DCMD_HAM_*`, `DCMD_MEMCLASS_*` marqués « used internally », non documentés (L) | devctl/about | observabilité audio/HA/mémoire par rétro-ingénierie des devctl |
| NET-01 | Sockets de domaine Unix (io-sock) **exigent un FS inscriptible** power-safe/Ext2/FFS3 (L) | migration 8.0.3 | service de relais UDS sans FS inscriptible ; très « embarqué sûr » |
| NET-02 | DIM (Dynamic Interrupt Manager) à activer **manuellement** pour le débit réseau (L) | migration 8.0.3 | auto-tuneur : bench + détection + activation selon la charge |
| TOY-01 | Utilitaires cibles remplacés par **toybox**, à linker commande par commande (L) | migration/command_line | suite de détection des divergences 7.1↔toybox pour scripts embarqués |
| MOUNT-01 | `mount_ifs` ne daemonize plus, `-b` déprécié ; nouvel IFS en mémoire via `-o` (L) | migration/command_line | vérificateur de scripts de boot + tests de régression amorçage |
| FS-01 | « Power-Safe filesystem compatibility » (qnx6fs) signalée comme point de migration 8.0.3 (L pointeur, S détail) | migration 8.0.3 | outil fsck/conversion qnx6fs→power-safe |
| IAPI-01 | IAPI expose PIDs, regs GP/FP, thread status, mappings, page tables, lecture mémoire — **rien** sur channels/connections/message passing, IRQs, stats CPU/IO par processus (L liste complète des 13 fonctions ; S pour l'absence) | introspection/apis+overview | « htop/pidin++ » de production sans `/proc`, orienté sûreté |
| IAPI-02 | Dumper **unique** système, exige `PROCMGR_AID_DUMPER` ; pas d'écriture mémoire exposée (L) | introspection/overview | service de core dump configurable : compression, chiffrement, dump sélectif, export réseau |
| IAPI-03 | Pas de flux d'événements cycle de vie (spawn/exit) — seuls les crashes notifiés (L liste ; S interprétation) | introspection/apis | daemon d'audit/surveillance de terminaison pour systèmes safety |
| LIBC-05 | Le livre C n'a **aucune matrice de conformité POSIX** (sommaire L : A–Z, manifests, charsets, safety ; S l'absence) | lib_ref/about | générateur de suite de conformité POSIX QNX + tableau de bord |

### (B) Conclusion (5 lignes)

1. **Oui, familles différentes** : la plus neuve est l'**outillage de portage/legacy** (LIBC-01→04, MIG-01, TOY-01) — rien de tel dans les 7 projets existants (sécurité, trace, OTA, vdev, WASM).
2. L'**IAPI est un vrai filon** : livre minuscule (13 fonctions), pensé « production/sûreté sans /proc », et tout l'observability moderne (connexions, canaux, IO, événements) est absent → outils diagnostics inédits.
3. Les classes devctl **obsolètes ou non documentées** (INPUT, PART, SND, PF/TAP/TUN renvoyés à FreeBSD) ouvrent une famille « ressource managers & réseau non outillé » distincte des vdev déjà trouvés.
4. Point important : **`inotify` existe en 8.0** (libfsnotify) — l'inventaire précédent est erroné ; timerfd/signalfd restent à vérifier (non vus).
5. Limite honnête : la **Discontinuation Notice (pages API/kernel/networking)** est le gisement le plus dense et m'était inaccessible (403 proxy) — à refaire, ~10 trous supplémentaires probables (S).

---

# TROUS NOUVEAUX n°2 (11/11 20:45) — System Architecture, Writing a Resource Manager, Programmer's Guide, Introspection API

Source : sous-agent ayant lu 13 pages (introspection_apis.html, overview.html,
ipc_Channels.html, ipc_Pulses.html, ipc_Typed_memory.html, ipc_Priority_inheritance_messages.html,
ipc_Server_boost.html, kernel_SchedulingAlgorithms.html, kernel_Sporadic_scheduling.html,
kernel_External_Code.html, kernel_CPU_offlining.html, resmgr about.html (ToC 12 chapitres),
prog about.html).

## Introspection API (IAPI) — correction : 14 fonctions, pas 13
- IA-CHAN : aucune fonction pour canaux / connexions / files Receive-Send-Reply [lu]
- IA-LIFE : pas de flux spawn/exit, uniquement polling de PID + événement coredump [lu]
- IA-DUMP : Dumper **unique** système, déclenché seulement sur terminaison anormale, tout-ou-rien, pas d'export réseau [lu]
- IA-STATS : zéro statistique cumulative par processus/thread (CPU, IPC, appels) [lu]
- IA-IRQ : rien sur les interruptions (handlers, comptes, latences) [lu]
- IA-RO : API en lecture seule, aucune écriture/injection → pas d'émulation de client ni de fault-injection [lu]
- SA-TYPED : mémoire typée sans aucune introspection (noms, tailles, utilisateurs) [lu + absence]

## Ordonnancement : mécanismes documentés, ZÉRO outil de vérification
- SA-SPOR : SCHED_SPORADIC documenté (« capped limit ») mais aucun outil d'observation du budget ni des replenishments ; l'automatisation est renvoyée à **MotionWise Schedule, hors SDP** [lu]
- SA-BOOST : « server boost » — ambiguïté écrite par QNX : « it's not clear which thread should be boosted » [lu]
- SA-PRIHER : héritage de priorité des messages **sticky** (ne redescend pas au reply), aucun outil de preuve [lu]
- SA-EXTCODE : le scheduler peut exécuter du code externe au noyau affectant le déterminisme, sans observation [sommaire]
- SA-CPUOFF : CPU offlining par app privilégiée, pas d'outil de vérification/monitoring [sommaire]
- SA-PULSE : pulses non bloquants et non queueables, aucun mécanisme de capture/rejeu [lu + absence]

## Resource managers : le trou le plus profond
- RM-SKEL : pas de générateur de squelette, le livre ne montre que des couches et exemples écrits à la main [lu]
- RM-TEST : **aucun** chapitre test / harnais / émulation de client / mesure de latence dans les 12 chapitres du livre [ToC exhaustif lu]
- RM-CONF : conformité non outillée, uniquement des conseils (« always at least one RECEIVE-blocked thread », « avoid leaving clients blocked indefinitely ») [sommaire]
- RM-LAT : Programmer's Guide sans chapitre de mesure IPC/latence ; timing.html ne traite que des « inaccuracies » du temps [ToC lu]

## Fausses alertes écartées par cet agent
- Trace/profilage : le chapitre Microkernel Instrumentation existe (procnto-smp-instr) + SAT/traceparser → PAS un trou.
- Sécurité des resmgr : le System Security Guide existe (livre séparé) → ne pas revendiquer de trou « validation des entrées ».
- Non vérifiés faute de budget : partitions APS, ASID, donneur de priorité, détail de la mémoire typée.

## Trois familles nouvelles (disjointes de tout ce qui précède)
1. Chaîne d'outillage resmgr : générateur + harnais + fuzzer + lint de conformité + banc de latence.
2. Introspection de production via IAPI : canaux, cycle de vie, stats, dump sélectif — l'API est annoncée « meant for production » mais aveugle à l'IPC.
3. Preuve d'ordonnancement : budget sporadique, héritage sticky, server boost ambigu, code externe, CPU offlining.

---

# TROUS NOUVEAUX n°3 (11/11 21:00) — HAM (High Availability Framework) et QPLMS
Source : sous-agent, 12 pages lues. Citation clé : la migration HAF→QPLMS impose de
« Holistically redesign the system's launch » — aucun convertisseur fourni.
**Rapport — trous HAM & QPLMS** (12 `web_fetch` utilisés, 12 pages **lues** ; rien d'autre parcouru)

## (A) Trous (16)

| # | Code | Trou | Page source | Pourquoi exploitable |
|---|------|------|-------------|----------------------|
| 1 | HAM-TEST | Aucun harnais de test/injection de pannes pour un handler HAM : le guide ne fournit que des listings d'exemples (restart, heartbeat, starvation), aucun outil pour simuler une panne et rejouer un scénario | examples.html, about.html (LU) | Un « chaos-HAM » QEMU/Pi5 qui tue/bloque/dégrade des processus et vérifie la réaction du handler = démonstration visuelle directe, zéro équivalent documenté |
| 2 | HAM-LAT | Aucune mesure de latence de reprise ni preuve de borne : rien ne timestamp ni n'analyse le délai détection→action→service restauré | hamover.html, examples.html (LU ; absence vérifiée sur les pages lues) | Mesurer et **prouver** « reprise < X ms » (combiné SAT/traceparser) = apport temps réel fort pour un jury |
| 3 | HAM-DECL | HAM se configure uniquement par API C, aucune configuration déclarative, aucun validateur du graphe entités/conditions/actions (cycles d'actions, conditions jamais armées, entités orphelines) | plms_migration_guide.html (« ham is configured by a C API »), hamover_HAMAPI.html (LU) | Un linter/générateur déclaratif de supervision HAM, vérifié en CI hôte, comble un vide outillage évident |
| 4 | HAM-DRIFT | La détection de dérive lente (fuite mémoire, latence métier qui dérive, deadline métier dépassée sans crash) repose sur des « external detectors » à écrire soi-même ; aucun détecteur fourni | hamover.html (LU : « permits external detectors to report interesting events ») | Bibliothèque de détecteurs prêts à l'emploi (seuils métriques, délais métier) branchés sur les conditions HAM = couche manquante entre supervision binaire et comportement fautif |
| 5 | HAM-FORK | Limite explicite : la lib HAM n'est pas fork()-sûre, appels inutilisables dans le fils avant exec*() | hamover_HAMAPI.html (LU) | Un shim/testeur qui détecte et signale les violations fork+HAM, ou wrapper sûr, cible un piège réel documenté |
| 6 | HAM-STARVE-P | Starvation couverte côté HAM (exemple dédié) mais **pas** côté QPLMS : plms ne surveille que heartbeat et mort, aucun contrôle de délai d'ordonnancement | examples.html (LU), plms_overview.html, config_plms.html (LU : task monitor = interval/max_miss seulement) | Ajouter une détection de starvation/délai métier à plms (via libplms + signaux) = trou fonctionnel net entre les deux services |
| 7 | PLMS-SPOF | plms n'a **pas de Guardian** (« since it does not have a guardian ») : contrairement à HAM, plms est un point de défaillance unique ; rien ne documente sa propre supervision | plms_migration_guide.html (LU), hamover.html (LU pour le contraste HAM/Guardian) | Prouver/outiller la résilience de plms lui-même (double instance, reprise, mesure) = sujet sécurité/temporalité inédit |
| 8 | PLMS-VALID | La vérif du DAG n'a lieu qu'au démarrage **sur la cible** (« PLMS parses the configuration file for correctness ») ; aucun validateur statique hôte (cycles, dépendances manquantes, includes cassés) avant le boot | plms_overview.html, config_plms.html (LU) | Validateur + visualiseur de DAG en CI/hôte : erreur détectée en secondes au lieu d'un boot raté sur Pi5 |
| 9 | PLMS-CRITPATH | Aucun outillage de mesure du chemin critique de démarrage : lancement parallèle affirmé mais pas de trace/Gantt de la file d'actions ni d'analyse du temps de boot résultant | plms_overview.html (LU : action queue, worker threads) | Extraire les événements slog2 → chemin critique + suggestions de parallélisation = lien direct avec Boot Optimization, mesurable sur Pi5 |
| 10 | PLMS-ATTACH | QPLMS ne peut pas superviser un processus déjà lancé (« QPLMS can't monitor an already-running process ») : tout processus démarré par `[+script]` ou SLM doit être relancé par plms | plms_migration_guide.html, scénario 4 (LU) | Pont « adopte sans relancer » (ou superviseur hybride SLM/script→plms) = trou fonctionnel explicitement reconnu par la doc |
| 11 | PLMS-MIGRATE | Migration HAF→QPLMS entièrement manuelle : « Holistically redesign the system's launch », aucun convertisseur des appels ham_* C vers une config plms, idem depuis boot script/slm | plms_migration_guide.html (LU) | Transpiler ham_*→composants plms (+ rapport de couverture des 5 scénarios) = outil de migration 8.0 concret, rien d'existant |
| 12 | PLMS-NOTIFY | Notifications QPLMS dégradées vs HAM : par classe d'événements, identité = **hash du nom** du composant (risque de collision, pas de pulse par entité/condition) | plms_migration_guide.html §Notifications (LU) | Couche de notification fiable (résolution de hash, routage fin) ou outillage de détection de collisions = limite documentée exploitable |
| 13 | PLMS-PRODKPI | Observabilité de production absente : plmsctrl est réservé « only on development and test systems », logs = slog2 debug ; aucun KPI de reprise (max_tries épuisés, FAULT, DSS) exploitable en prod | plms_migration_guide.html (LU), plms_overview.html (LU) | Exporter états/KPI vers un superviseur externe (l'API NOTIFY existe mais est fruste) = famille « introspection de production » nouvelle |
| 14 | PLMS-APS8 | `aps` non supporté en SDP 8.x (uniquement QOS 2.2.x) : les composants plms ne peuvent pas être assignés à une partition APS en 8.0 ; `-W` (runmask workers) perdu, remplacé par `cluster`/`-C` | usage_differences.html (LU) | Démontrer/contourner l'impact ordonnancement en 8.0 (priorités 1-253, cluster) ou outiller le mapping APS↔plms = trou certitude temps réel |
| 15 | PLMS-DSS | Sémantique de récupération grossière : repair = NONE/STOP/RESTART/FAULT/DSS avec DSS = `sysmgr_reboot()` complet ; pas de dégradation graduelle ni de restauration d'état du processus重启é | plms_overview.html, config_plms.html (LU) | Politiques de reprise à paliers (redémarrer le module, basculer en mode dégradé avant reboot) + checkpoint d'état = valeur sécurité démontrable |
| 16 | HAM-CFG-SLM | Chevauchement HAM/SLM/plms non outillé : la doc cite slm/boot scripts comme « current launcher » à migrer, mais rien n'aide à arbitrer ou détecter les doublons de supervision (même processus gardé 2×) | plms_migration_guide.html (LU) ; **supposé** : rôle exact de SLM non relu ici | Audit des configurations (qui garde quoi, HAM vs plms vs SLM vs [+script]) = outil d'intégration système inédit |

## (B) Déjà couvert (ne pas reproposer)
- HAM/Guardian : résilience du HAM lui-même par miroir en mémoire partagée (hamover.html, LU).
- Exemples HAM fournis : simple/compound restart, death notification, heartbeat/liveness, starvation (examples.html, LU).
- API HAM ~35 fonctions, thread-safe et cancellation-safe (parts.html, hamover_HAMAPI.html, LU).
- QPLMS : DAG de dépendances (`depend`, `module`), lancement parallèle (action queue + workers), watchdog heartbeat via mémoire partagée anonyme, mort/relance avec max_tries/wait_time, états riches dont DSS, mémoire pré-allouée, certifié safety (plms_overview.html, config_plms.html, LU).
- plmsctrl (debug uniquement), logs slog2info -b plms, -v (plms_migration_guide.html, LU).
- Lancement sécurisé dans la config : stype, ability, aslr, rlimits, groups/user, -U/-t avec secpol (config_plms.html, plms_migration_guide.html, LU) — rejoint la chaîne secpol déjà fournie.
- Guide de migration HAF→QPLMS avec 5 scénarios + notifications (LU) ; table de différences QOS 2.2.x/SDP 8.x (LU).

## (C) Conclusion (familles nouvelles ?)
1. **Oui — introspection/observabilité de production** : plmsctrl interdit en prod, aucun KPI de reprise, notifications par hash : famille distincte de l'IAPI existante (trous 7, 12, 13).
2. **Oui — preuve & mesure temporelle de la reprise** : latence de reprise, borne prouvée, chemin critique de boot DAG, aps absent en 8.0 : parent de « preuve d'ordonnancement » mais appliqué à la supervision, jamais couvert (2, 9, 14).
3. **Oui — migration 7.1/2.2→8.0 outillée** : transpiler ham_*→plms, arbitrage HAM/SLM/[+script], validateur de config hôte : la doc impose un redesign manuel (3, 8, 11, 16).
4. **Non nouveau** : politiques de sécurité (stype/ability déjà dans la config), images/OTA, vdev, WebAssembly — rien dans ces deux guides ; « outillage des gestionnaires de ressources » n'est qu'effleuré (HAM/plms ne sont pas des RM), donc à classer comme famille **supervision/HA**, réellement nouvelle.

---

# TROUS NOUVEAUX n°4 (11/11 21:05) — Device Publishers (RMPS), capteurs, HID, audio
## Trous — Device Publishers (RMPS), capteurs, HID, audio — QNX SDP 8.0

**Pages lues** (www.qnx.com/developers/docs/8.0/) : `dev_pub` about, overview, rmps_objects, plugins, usblauncher_otg ; nav `guides.html`, `references.html`, `programming.html`. **Non lues** : usblauncher_usage, drivers, plugin_ratings, graphics.html, technotes, listes A–Z des utilitaires → les « absences » ci-dessous sont *non rencontrées dans les pages lues*, pas prouvées exhaustivement.

### (A) Trous

| CODE | Trou | Source | Exploitable |
|---|---|---|---|
| PUB-SDK | Aucune API/SDK « écrire un publisher » : le guide ne décrit que le *contenu des objets RMPS* et les options CLI | dev_pub/about.html (lu) | Kit open-source : lib de publication RMPS + générateur de publisher |
| PUB-SENS | Un seul publisher livré : `usblauncher_otg` (USB/stockage/média) ; rien pour capteurs, I2C/SPI, BLE, batterie, thermique | dev_pub/overview.html (lu) | Publisher de capteurs pour HAT RPi 5, gros besoin hackathon |
| PUB-SIM | Aucune simulation/test sans matériel mentionnée dans tout le guide ; pas de publisher virtuel pour QEMU | dev_pub/about.html (lu, sommaire complet) | `fake-usblauncher`/injecteur RMPS pour QEMU = démo sans hardware |
| PUB-CONF | Aucun validateur de conformité des objets RMPS (arborescence « fixed locations » imposée mais non outillée) | dev_pub/rmps_objects.html (lu) | Linter/vérificateur de schéma RMPS réutilisable |
| PUB-LAT | Rien sur la latence de publication, horodatage des notifications ou QoS pub/sub | dev_pub/rmps_objects.html (lu) | Banc de mesure horodatée attach→objet RMPS→abonné |
| PUB-ALARM | Aucune priorité, arbitrage ou sémantique d'alarme : l'objet « device control » accepte des commandes, « peut contenir les résultats », sans file prioritaire ni préemption | dev_pub/rmps_objects.html (lu) | Voir (C) : couche d'arbitrage au-dessus de RMPS |
| PUB-META | Modèle de données orienté média/stockage (mountpoint, partitions, TOC, « temperature/drive mechanism » du disque) : pas d'unités, plages, calibration, timestamps de capteur | dev_pub/rmps_objects.html (lu) | Extension du schéma pour données physiques normalisées |
| PUB-PLUG | Plugins (generic, ipod, mediafs, audiocd, dvd) tous média ; pas d'API de rédaction ni d'exemple cités ; ratings auto-déclarés | dev_pub/plugins.html (lu) | SDK+exemple de plugin non-média (ex. métadonnées capteur) |
| PUB-LIFE | Publishers « persistent background processes… you can restart » mais aucune intégration HAM/lifecycle documentée | dev_pub/overview.html (lu) | Superviseur HAM générique pour publishers |
| PUB-SEC | Aucune permission/secpol mentionnée pour les objets RMPS — y compris l'objet de commande (couper l'alim d'un port USB) | dev_pub/rmps_objects.html (lu) | ACL + politique secpol pour `/usb/launcher/command/` |
| USB-OTG | Protocoles OTG ADP/SRP/HNP non supportés, « software emulation » seulement | dev_pub/usblauncher_otg.html (lu) | Gestion USB-PD/rôles par software |
| USB-GADGET | Mode device limité à CarPlay (module Apple séparé) ; pas de gadget générique (UAC2, MTP, HID gadget) | dev_pub/usblauncher_otg.html (lu) | Publisher/gadget USB générique pour Pi 5 |
| SENS-ABS | GPIO et SPI ont des frameworks documentés, mais aucune abstraction capteur au-dessus (fusion, calibration, découverte) | nav/references.html (lu) | « libsensors » QNX au-dessus de GPIO/SPI + publisher |
| AUD-DOC | **Zéro** doc audio dans SDP 8.0 : pas d'io-audio, d'audio DDK, d'`asound`, de codecs dans guides/references/programming ; le multimédia vit dans un paquet séparé « Multimedia for QNX SDP » | nav/guides.html, nav/references.html, nav/programming.html (lus) ; mention du paquet dans usblauncher_otg.html (lu) | Tout projet audio SDP-only est greenfield : serveur/mixage à échéance garantie, mesure de latence bout-en-bout, codecs |
| HID-DOC | Aucune doc HID/input dans le nav SDP (io-input, pilotes HID absents des guides lus) — réserve : graphics.html (Screen) non consulté | nav/guides.html, references.html (lus) | Publisher HID + outil de test clavier/souris sur QEMU |

### (B) Déjà couvert — fausses alertes évitées
- **Un publisher existe et est documenté** (`usblauncher_otg`, objets device/command/driver/mount, montage auto via `rules.mnt`) — ne pas proposer « framework de publication inexistant ».
- **Mécanisme de plugins avec manager et système de ratings** — le trou est l'API de rédaction, pas le mécanisme.
- **Objet de commande RMPS** (ex. power du hub) — le trou est l'arbitrage/priorité, pas les commandes.
- **Frameworks GPIO et SPI documentés** — le bus est couvert ; seule l'abstraction capteur manque.
- **Introspection API et SAT existent** (nav lu) — ne pas les reproposer.
- **Audio/Multimédia** : probablement fourni hors SDP (« Multimedia for QNX SDP », Apple Device Support) — le trou est *dans SDP*, pas « QNX n'a pas d'audio ». io-audio/asound dans les utilitaires A–Z : non vérifié (budget).

### (C) Alarmes / événements prioritaires — réponse explicite
**Non, le framework RMPS ne couvre ni la gestion ni l'arbitrage d'alarmes.** Pages lues : RMPS est un pub/sub d'*informations périphériques* (nom brut, mountpoint, partitions, bus/slot) ; l'objet « device control » accepte des commandes et « can also contain command outcomes » — aucune notion de priorité, préemption, file d'événements, criticité ou arbitrage inter-dispositifs n'apparaît (rmps_objects.html, overview.html, plugins.html, usblauncher_otg.html). **Le projet d'arbitre d'alarmes IEC 60601-1-8 n'est donc pas rendu redondant** ; RMPS peut au plus servir de transport de présence périphérique en amont de l'arbitre.

### (D) Conclusion (familles nouvelles ?)
1. **Oui — famille inédite** : « écosystème de publication périphériques/capteurs » (SDK publisher, simulateur QEMU, validateur RMPS, publishers capteurs) ne recoupe aucune des 8 familles listées.
2. **Audio SDP-only = quasi nouvelle famille** : rien de documenté dans SDP 8.0, donc mixage à échéance garantie, latence et codecs sont à reconstruire — très différenciant.
3. L'arbitre d'alarmes médicales **reste valide** et gagne un ancrage officiel : RMPS comme source d'événements, l'arbitrage comme contribution propre.
4. Ponts possibles avec l'existant : publisher USB virtuel ↔ « vdev manquants », superviseur HAM des publishers ↔ « outillage des gestionnaires de ressources ».
