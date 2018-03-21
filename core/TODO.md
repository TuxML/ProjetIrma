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


---
TuxML incremental :
./tuxml --increment nInc    //nInc : nombre d'itérations
  --> compile une config de base (randconfig)
  --> sauvegarde les fichiers compilés dans un dossier
  --> itère sur nInc et lance nInc compilations (randconfig)
    --> entre chaque compil on remet les fichiers compilés de config_base

  à terme faire une "smart mutation" à chaque itération

./tuxml --no-clean base.config inc.config
  --> compile base.config puis compile inc.config sans clean
