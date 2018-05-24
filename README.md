Last updates:<br>
README - May the 24th 2018<br>
Prod docker image - May the 22th 2018 ( see https://github.com/TuxML/ProjetIrma/releases )

# TuxML
## MLfood.py script
### Goal

`MLfood.py` is the first command to run on your host machine.

At the beginning, it will ask you the super user privileges in order to run docker.

This script is used to fill the DataBase which "feed" the Machine Learning algorithm and allows to start automatically the `tuxml.py` command on different dockers by calling the script `tuxLogs.py` which write output.log.

`./MLfood <Integer>` will start n docker sequentially, each docker run `tuxlogs.py` which run `tuxml.py`

### How to use ?

Command should be :

    ./MLfood.py <Integer> [<Integer>] [Options]

    Example : ./MLfood 50 5 --dev

This example will run 50 docker, each one will run 5 compiling in incremental mode in addition to the first one, on the developpement docker image ("--dev").

```
A simple run command could be:

./MLfood 100

```

It will start 100 compiling sequentially on the functionnal docker image.

```
  The first Integer run MLfood into the given number of containers
  The second Integer is optional, it is used in a case of incremental compiling with <Integer> number of compiling in a container.
  The default number of compiling in a container is set as 1
  Options: --no-clean    Do not delete used containers
           -h, --help    Show this help
           --reset-logs  Delete all the saved logs
           --dev         Use images in current developpement
           --force_compilation_limits To not display user warning in case of large number of compilations
           --no-check-log Do not compute the size of Logs directory.
           --silent      Do not print the process of compilation, only display when a new container is created and the end of total computation.
```

The script retrieves the logs file err.logs, std.logs and output.logs as well as the `.config` file generated in the RandConfig command in the Logs/ folder thanks to `tuxLogs.py`.

`MLfood.py` now use "tee" to create the output.logs from `tuxLogs.py` to prompt the output and create the `output.logs` which is the tuxml.py's one.

See `tuxLogs.py`

```
MLfood.py [-h] [--no-clean] [--reset-logs] [--dev] [--force-compilation-limits] [--no-check-log] [--silent] nbcompil [incremental]

```

## tuxml.py script
### Goal
The TuxML's goal is to automatically compile Linux kernel sources in order to build
a database for a machine learning algorithm. If the compilation crashes, TuxML analyzes the error log file to determine the causes.

There are two possible ways:  

* it is a missing  package : TuxML will install it and  resume the compilation
* the error can't be fixed : the compilation stops

If the compilation is a success, TuxML launch a kernel boot test.

Then it sends the results to the TuxML database.

You can run TuxML independantly from the MLfood.

### How to use ?
```
usage: tuxml.py [-h] [-v {1,2,3,4}] [-V] [-c NB_CORES] [-d KCONFIG]
                [--incremental NINC] [--database {prod,dev,alexis}]
                source_path

positional arguments:
  source_path           path to the Linux source directory

optional arguments:
  -h, --help            show this help message and exit
  -v {1,2,3,4}, --verbose {1,2,3,4}
                        increase or decrease output verbosity
                          1 : very quiet
                          2 : quiet
                          3 : chatty (default)
                          4 : very chatty
  -V, --version         display TuxML version and exit
  -c NB_CORES, --cores NB_CORES
                        define  the  number  of CPU  cores  to  use  during  the
                        compilation. By default  TuxML  use all  the  availables
                        cores on the system.
  -d KCONFIG, --debug KCONFIG
                        the KCONFIG_FILE given.
  --incremental NINC    incremental  mod does  not  erase  files  from  previous
                        compilations. The  NINC  parameter  corresponds  to  the
                        number of incremental compilation to launch.
  --database {prod,dev}
                        choose on which database send the compilation results
```

## TPDIM.py

### Goal
This script aims to build a Docker image for using TUXML.
Mainly for developers of TUXML that maintain the Docker images: https://hub.docker.com/r/tuxml/tuxmldebian/tags/  

### How to use ?

The simple way is to use
``` ./TPDIM -a debian -t 'tag-name'```

It executes all following procedures (generate, build and push):
 * Generation : Use only when update Dockerfile or when adding new dependencies to the image ``` ./TPDIM -g debian -dep dependences.txt -t 'tag-name'```
 * Build : ``` ./TPDIM -b debian -t 'tag-name'```
 * Push : ``` ./TPDIM -p debian -t 'tag-name'```

Have a look at option for customizing e.g., the image (e.g. debian) or the tag (e.g., dev or prod).

## License
The TuxML project is licensed under the terms of the **Apache License 2.0** as available in the `LICENSE` file and [online here](http://www.apache.org/licenses/LICENSE-2.0.txt). A list of contributors and other details are available in the `NOTICE.md` file.
