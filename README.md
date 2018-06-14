Last updates:<br>
README - June the 13th 2018<br>
Prod docker image - June the 14th 2018 ( see https://github.com/TuxML/ProjetIrma/releases )

# TuxML
## MLfood.py script
### Goal

`MLfood.py` is the first command to run on your host machine.

At the beginning, it will ask you the super user privileges in order to run docker.

This script is used to fill the DataBase which "feed" the Machine Learning algorithm and allows to start automatically the `tuxml.py` command on different dockers by calling the script `runandlog.py` which write output.log, the complete terminal output from the beginning of tuxml.py to its end.

`./MLfood <Integer>` will start n docker sequentially, each docker run `runandlog.py` which run `tuxlogs.py` that run `tuxml.py`

### How to use ?

Command should be :
  ```
  ./MLfood.py <Integer> [<Integer>] [Options]

  Example : ./MLfood.py 50 5 --dev
  ```
This example will run 50 docker, each one will run 5 compiling in incremental mode in addition to the first one, on the developpement docker image ("--dev").

```
A simple run command could be:

./MLfood.py 100

```

It will start 100 compiling sequentially on the functionnal docker image.

```
A more complexe command could be:

sudo ./MLfood.py 100 10 --dev --fetch-kernel --no-clean --force-compilation-limits --no-logs --silent
```

* `sudo` : in order to run the entire process without asking for super user password during it ( sending to database for instance )

* `./MLfood.py 100 10` To run 100 new containers and run in it 1 basic compilation plus 10 incrementals next. So 1100 compilations.

* `--dev` To use the developpement docker image. ( Can be unstable and down )

* `--fetch-kernel` Used to retrieves the kernel generated and its compressed versions. ( May be heavy, be careful to not fulfill your hard drive )

* `--no-clean` Do not clean the all 100 Docker containers, takes place in memory.

* `--force-compilation-limits` To pass the demand to the user if he is sure to run more than 50 compilations.

* `--no-logs` Do not keep local logs during the all process. ( Logs are still sent to the database )

* `--silent` To run MLfood without show the intern process, only the current Docker containers.


The first Integer run MLfood into the given number of containers.
The second Integer is optional, it is used in a case of incremental compilation with <Integer> number of compilation in a container.
The default number of compilations in a container is set as 1

```
Options:

positional arguments:
  nbcompil              Run MLfood into the given number of containers.
  incremental           Used in a case of incremental compilation with
                        <Integer> compilation in a container.

optional arguments:
  -h, --help            show this help message and exit
  --no-clean            [dev] Do not delete past containers.
  --reset-logs          Delete all the saved logs and exit.
  --dev                 [dev] Use image in current development.
  --force-compilation-limits
                        Use this option to pass the user check if the
                        requested number of compilations exceeds 50.
  --no-check-log        [dev] Do not compute the Logs folder size at the end
                        of compilation.
  --silent              Do not print on standard output. Used to compute only
                        without printing
  --fetch-kernel        [dev] Fetch vmlinux kernel from the Docker container (
                        Be careful to not overload your hard drive )
  --no-logs             Do not create local logs
```

The script retrieves the logs file err.logs, std.logs and output.logs as well as the `.config` file generated in the RandConfig command in the Logs/ folder thanks to `runandlog.py`.

See `runandlog.py`

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
