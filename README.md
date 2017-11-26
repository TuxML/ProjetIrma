# py-scripts

## tuxml.py
```
usage: tuxml.py [-h] [-v] [-V] [-d [KCONFIG_SEED]] source_path

Welcome, this is the TuxML core program. It's currently a pre-alpha. Please
visit our Github at https://github.com/TuxML in order to report any issue.
Thanks !

positional arguments:
  source_path           path to the Linux source directory

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         increase output verbosity
  -V, --version         display TuxML version and exit
  -d [KCONFIG_SEED], --debug [KCONFIG_SEED]
                        debug a given kconfig seed. If no seed is given, TuxML
                        will use the existing kconfig file in the linux source
                        directory
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
* ~~renommer installDependencies.py en tuxml_depman.py~~
* ~~adapter tuxml_depman.py aux nouvelles fonctions de tuxml_common.py~~
* utiliser tuxml_settings.py dans tuxml_sendDB.py
* "fusionner" get_distro() et get_package_manager()

## MLfood.py

Script used to fill the DataBase which "feed" the Machine Learning algorithm.
Allows to start automatically the tuxml.py command on different dockers by calling
the script tuxLogs.py which write the tuxml.logs.

Command should be :

    ./MLfood.py <Integer> [Options]

It will start \<Integer\> number of compilation sequentially.

```
Options : --no-clean      Do not delete past containers
          -h, --help      Prompt Options
          --reset-logs    Delete all the logs in Logs/
```

[UPDATE] The script will now retrieves the logs file err.logs, std.logs and output.logs in the Logs/ folder.
thanks to tuxLogs.py.

## TPDIM(WIP)

This script/program is design to help people using TuxML easly manage there docker image or container.

At the moment the script can do :

* Build the docker image tuxml/tuxmldebian
* Push this image on the repository tuxml on
