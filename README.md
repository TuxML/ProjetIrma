# TuxML


## How to Use

To run the main command on a host machine, you just need to download `MLfood.py`, the folders "core" and "csvgen" are contained in the image for docker.
Running `MLfood.py` download the latest image with the TuxML folder.



## MLfood.py

`MLfood.py` is the first command to run on your host machine.

At the beginning, it will ask you the super user privileges in order to run docker.

This script is used to fill the DataBase which "feed" the Machine Learning algorithm and allows to start automatically the `tuxml.py` command on different dockers by calling the script `tuxLogs.py` which write the tuxml.logs.

./MLfood n will start n docker sequentially, each docker run `tuxlogs.py` which run `tuxml.py`

Command should be :

    ./MLfood.py <Integer> [Options]

It will start \<Integer\> number of compilation sequentially.

```
Options : --no-clean      Do not delete past containers
          --reset-logs    Delete all the logs in Logs/
          -h, --help      Prompt Options for MLfood.py
```

The script retrieves the logs file err.logs, std.logs and output.logs as well as the `.config` file generated in the RandConfig command in the Logs/ folder thanks to `tuxLogs.py`.

`MLfood.py` now use "tee" to create the output.logs from `tuxLogs.py` to prompt the output and create the `output.logs` which is the tuxml.py's one.

See `tuxLogs.py`

## tuxLogs.py

Script contained in the docker image in the folder/TuxML, this is the script which run the command `/TuxML/core/tuxml.py /TuxML/linux-4.13.3 -v` directly.

This script exist only to allow `MLfood.py` to create the output log of `tuxml.py` with the stack trace.

See `MLfood.py`


## tuxml.py
```
usage: tuxml.py [-h] [-v] [-V] [-d [KCONFIG_SEED]] source_path

Welcome, this is the TuxML core program.

The goal of TuxML is to  automatically  compile Linux kernel sources in order to
build a database for a machine learning algorithm.
If the compilation crashes, TuxML  analyzes the error log file  to determine the
causes. There are two possible ways:
  * it is a missing  package : TuxML will install it and  resume the compilation
  * the error can't be fixed : the compilation stops
Then TuxML sends the results of the compilation to the database.

Keep in mind that the program is currently  in developpement stage. Please visit
our Github at https://github.com/TuxML in order to report any issue.
Thanks !

positional arguments:
  source_path           path to the Linux source directory

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         increase output verbosity
  -V, --version         display TuxML version and exit
  -d [KCONFIG_SEED], --debug [KCONFIG_SEED]
                        debug a given  kconfig seed. If no seed is given, TuxML
                        will use the existing kconfig file in  the linux source
                        directory
```

### Expected output

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

### Todolist

* ~~renommer sendDB.py en tuxml_sendDB.py~~
* ~~renommer installDependencies.py en tuxml_depman.py~~
* ~~adapter tuxml_depman.py aux nouvelles fonctions de tuxml_common.py~~
* ~~utiliser tuxml_settings.py dans tuxml_sendDB.py~~
* ~~"fusionner" get_distro() et get_package_manager()~~
* ~~étendre l'argument `--debug` pour qu'il supporte aussi un chemin vers un .config spécifique.~~

## TPDIM.py (WIP)

This script/program is design to help people using TuxML easly manage there docker image or container.

At the moment the script can do :

* Build the docker image tuxml/tuxmldebian
* Push this image on the repository tuxml on

## License

The TuxML project is licensed under the terms of the **Apache License 2.0** as available in the `LICENSE` file and [online here](http://www.apache.org/licenses/LICENSE-2.0.txt). A list of contributors and other details are available in the `NOTICE.md` file.
