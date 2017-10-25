# py-scripts

### tuxml.py
    ./tuxml.py source_directory [--debug] [--version]

expected output :

    [*] Cleaning previous compilation
    [*] Generating random config
    [*] Checking dependencies
    [*] Compilation in progress
    [+] Compilation done
    [+] Testing the kernel config
    [+] Successfully compiled in 00:10:45, sending data
    [*] Sending config file and status to database
    [+] Successfully sent info to db


### MLfood.py

  Script de lancement de remplissage de la BdD pour "nourrir" l'algorithme de Machine Learning.
  Permet de lancer automatiquement la commande tuxml.py sur différentes conteneurs ( Docker ) soit le lancement de tuxml sur différentes architectures en parallèle.

  La commande doit être :

    python3 MLfood.py [nbentier]
