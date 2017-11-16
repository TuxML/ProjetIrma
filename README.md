# py-scripts

## tuxml.py
```
[*] USE : sudo ./tuxml.py </path/to/sources/directory> [option1 option2 ...]
[*] Available options :
        -d  --debug             TuxML is more verbose
        -h  --help              Print this
            --no-randconfig     Do not generate a new config file
        -v  --version           Display the version of TuxML
```

Expected output :

```
[*] Cleaning previous compilation
[*] Generating random config
[*] Checking dependencies
[*] Compilation in progress
[+] Compilation done
[+] Testing the kernel config
[+] Successfully compiled in 00:10:45, sending data
[*] Sending config file and status to database
[+] Successfully sent info to db
```

### Changelog v0.2
**\*** Refactoring du code : le script tuxml.py a été préparé pour pouvoir diviser le dev sur plusieurs branches (master, arch-support-addition, redhat-support-addition, etc) --> fonctions build_dependencies_\*()  
**\*** Certaines parties de tuxml.py ont été remplacées par des fonctions développées pour installDependencies.py (install_missing_packages())  
**\*** Les fichiers de logs sont désormais de la forme *err_\<timestamp\>.logs* et *std_\<timestamp\>.logs*  
**\+** tuxml_common.py : contient les fonctions communes à plusieurs scripts  
**\+** tuxml_settings.py : contient les variables globales  
**\+** Ajout de la date et de l'heure en mode debug dans les logs de tuxml.py (désormais il faut utiliser le pretty printer)  
**\-** L'appel à sendDB a été désactivé temporairement car le site est H.S

**TODO :**

* ~~renommer sendDB.py en tuxml_sendDB.py~~
* ~~renommer installDependencies.py en tuxml_init.py~~
* adapter tuxml_init.py aux nouvelles fonctions de tuxml_common.py
* utiliser tuxml_settings.py dans tuxml_sendDB.py
* "fusionner" get_distro() et get_package_manager()

## MLfood.py

Script used to fill the DataBase which "feed" the Machine Learning algorithm.
Allows to start automatically the tuxml.py command on different dockers by calling
the script tuxLogs.py which write the tuxml.logs.

Command should be :

    ./MLfood.py [Integer]

It will start [Integer] number of compilation sequentially.

[UPDATE] The script will now retrieves the logs file err.logs, std.logs and tuxml.logs in the Logs/ folder
thanks to tuxLogs.py.


## TPDIM(WIP)

This script/program is design to help people using TuxML easly manage there docker image or container.

At the moment the script can do :

* Build the docker image tuxml/tuxmldebian
* Push this image on the repository tuxml on https://hub.docker.com/r/tuxml/
