# TuxML
## MLfood.py script
### Goal

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

### How to use ?
```
usage: MLfood.py [-h] [-b BRANCH] [-i IMAGE] [--no-clean] [-V] [-v {0,1,2}]
                 NB_DOCKERS

positional arguments:
  NB_DOCKERS            number of dockers to launch, minimum 1

optional arguments:
  -h, --help            show this help message and exit
  -b BRANCH, --branch BRANCH
                        choose which  version of TuxML to  execute between
                        master and dev
                          master : last stable version (default)
                          dev    : last up-to-date version
  -i IMAGE, --image IMAGE
                        two kinds of images are available
                          prod : TuxML is  already included in the docker image.
                                 This is the fastest way. (default)
                          dev  : download  TuxML repository  from  GitHub before
                                 starting the compilation
  --no-clean            do not clean containers
  -V, --version         display the sampler version and exit
  -v {0,1,2}, --verbose {0,1,2}
                        increase or decrease output verbosity
                          0 : quiet
                          1 : normal (default)
                          2 : chatty
```

## tuxml.py script
### Goal
The goal of TuxML is to  automatically  compile Linux kernel sources in order to build a database for a machine learning algorithm.  
If the compilation crashes, TuxML  analyzes the error log file  to determine the causes. There are two possible ways:  

* it is a missing  package : TuxML will install it and  resume the compilation
* the error can't be fixed : the compilation stops

Then TuxML sends the results of the compilation to the TuxML database.

You can run TuxML independantly from the sampler.

### How to use ?
```
usage: tuxml.py [-h] [-v] [-V] [-d [KCONFIG_SEED]] source_path

positional arguments:
  source_path           path to the Linux source directory

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         increase output verbosity
  -V, --version         display TuxML version and exit
  -d [KCONFIG_SEED], --debug [KCONFIG_SEED]
                        debug a given  kconfig seed. If no seed is given, TuxML
                        will use the existing kconfig file in  the linux source
                        directhttps://github.com/TuxML/MCManagerory
```

## TPDIM.py

### Goal
This script/program is design to help people using TuxML to easly manage there docker image or container.

### How to use ?

You have to use few command to build and push :
* Build : ``` ./TPDIM -b [IMAGE_NAME : debian] -t [TAG_NAME]```
* Push : ``` ./TPDIM -p [IMAGE_NAME : debian] -t [TAG_NAME]```
* Generation : Use only when update Dockerfile or when adding new dependences to the image ``` ./TPDIM -g [IMAGE_NAME : debian] -dep dependences.txt -t [TAG_NAME]```