# Scripts
## Core
### tuxml.py
* ~~soustraire le temps d'installation des paquets~~
* intégrer les tests du noyau

### tuxml_common.py
* ~~dnf, yum : faire un check-update au lieu d'un update~~

### tuxml_environment.py
* ~~ajouter dans l'environnement *compilation* les infos : **branch** (dev/master) et **image** (dev/prod)~~
* supprimer la parenthèse dans libc_version et gcc_version (env compilation) quand on est sur Debian
* récupérer le type de disque

### tuxml_depman.py
* fusionner les fonctions build_dependencies : debian, arch, redhat
* vérifier le package est déjà présent avant de l'ajouter dans missing_packages
* install des paquets pas auto pour dnf
