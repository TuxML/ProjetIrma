# Scripts
## Core
### tuxml_environment.py
* ajouter dans l'environnement *compilation* les infos : **branch** (dev/master) et **image** (dev/prod)
* supprimer la parenthèse dans libc_version et gcc_version (env compilation) quand on est sur Debian

### tuxml_depman.py
* fusionner les fonctions build_dependencies : debian, arch, redhat
* vérifier le package est déjà présent avant de l'ajouter dans missing_packages
* install des paquets pas auto pour dnf

## Sampler
* envoyer les logs : err, std, output et .config
* séparer run_tuxml() en 2 fonctions
  - download_tuxml()
  - run_tuxml()

# Docker
* Créer les images (dev) :
  - fedora
  - centos
  - ubuntu
  - manjaro

  Pour chaque image, installer les paquets suivants (ou équivalents) : *wget, apt-file, python3, python3-pip, libmariadbclient-dev, git*
