# TuxML

## sampler.py script
### Goal
The sampler allows you to run tuxml.py through many docker images sequentially.

At the end of the tuxml execution, the sampler retrieves the logs (standard, error, tuxml's output and kconfig file) from the docker container and saved them to the Tuxml/logs folder.

### How to use ?
```
usage: sampler.py [-h] [-v {0,1,2}] [--no-clean] NB_DOCKERS IMAGE BRANCH

positional arguments:
  NB_DOCKERS            number of dockers to launch, minimum 1
  IMAGE                 two kinds of images are available
                          prod : TuxML is  already included  in the docker
                                 image (faster than dev)
                          dev  : download  TuxML  repository  from  GitHub
                                 before starting the compilation
  BRANCH                choose which  version of TuxML to  execute between
                        master and dev
                          master : last stable version
                          dev    : last up-to-date version

optional arguments:
  -h, --help            show this help message and exit
  -v {0,1,2}, --verbose {0,1,2}
                        increase or decrease output verbosity
                          0 : quiet
                          1 : normal (default)
                          2 : chatty
  --no-clean            do not clean containers
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
                        directory
```
