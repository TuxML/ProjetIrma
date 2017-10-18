# py-scripts

## Scripts

### send_config_http.py
Envoie une entrée à la bdd jhipster, puis fait un select pour voir toutes les entrées. Pour vérifier que ça marche la commande devrait retourner un 201 Created et un 200 OK avec un tas de données en JSON entre les deux.

### tuxml.py
    ./tuxml.py path/to/kernel/sources


### MLfood.py

  Script de lancement de remplissage de la BdD pour "nourrir" l'algorithme de Machine Learning.
  Permet de lancer automatiquement la commande tuxml.py sur différentes conteneurs ( Docker ) soit le lancement de tuxml sur différentes architectures en parallèle.
