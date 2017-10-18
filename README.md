# py-scripts

## Scripts

### send_config_http.py
Envoie une entrée à la bdd jhipster, puis fait un select pour voir toutes les entrées. Pour vérifier que ça marche la commande devrait retourner un 201 Created et un 200 OK avec un tas de données en JSON entre les deux.

### tuxml.py
    ./tuxml.py path/to/kernel/sources
    
expected output :

    [*] Checking dependencies
    [*] Waiting for compilation ending...
    [+] Compilation done
    [+] Successfully compiled, sending data
    [*] Sending config file and status to database
    [+] Successfully sent info to db


