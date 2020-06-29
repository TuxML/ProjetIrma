# TuxML: Machine Learning and Linux Kernel


The goal of TuxML is to predict properties of Linux Kernel
configurations (e.g., does the kernel compile? what's its size? does
it boot?).  The Linux Kernel provides nearly 15000 configuration
options: there is an infinity of different kernels.  As we cannot
compile, measure, and observe all combinations of options (aka
configurations), we're trying to learn Linux kernel properties out of
samples of configurations. See talk at Embedded Linux Conference
Europe in 2019:

[![Alt
text](https://img.youtube.com/vi/UBghs-cwQX4/0.jpg)](https://www.youtube.com/watch?v=UBghs-cwQX4)

**You can easily loan your machine and contribute if you want, just
  copy and paste the line below!**

<img align="right" width="100" height="100"
src="miscellaneous/informations/tuxml_logo_small.png" alt="TuxML's
Logo"/>

The goal of the TuxML team is to develop tools, mainly based on Docker
and Python, to massively compile and gather data about thousand of
kernel configurations.  The TuxML name comes from the combination of
[Tux](https://en.wikipedia.org/wiki/Tux_(mascot)), the mascot of the
Linux Kernel, and ML for statistical Machine Learning.

## I want to help by compiling some Linux kernels!

Requirements : `Python3` and `Docker` are needed (do not forget to
start the docker service usually with `sudo service docker start`).

```bash
wget https://raw.githubusercontent.com/TuxML/ProjetIrma/dev/kernel_generator.py ; python3 kernel_generator.py --dev 1
```

Copy this command and run it in a terminal. It will send compilation
results to our database.  You can modify the 1 parameter to any other
number (it's the number of kernels your machine will compile).  The
python script gives you some other options that you can use, see [this
page for
more](https://github.com/TuxML/ProjetIrma/wiki/User_documentation#python-script-entry-point--kernel_generatorpy).

For a more up-to-date version of TUXML, please consider the **dev
branch**

## I want to know more about the project!

Please check our [wiki](https://github.com/TuxML/ProjetIrma/wiki).

## Contributors' list

* [Mathieu Acher](http://www.mathieuacher.com/) (University Rennes 1, INRIA, CNRS, IRISA), scientific leader
* [DiverSE team (INRIA/IRISA research team)](http://www.diverse-team.fr/)
* [ANR VaryVary project](https://varyvary.github.io/)
* Master 1's team of 2017-2018 :
  - Corentin CHÉDOTAL
  - Gwendal DIDOT
  - Dorian DUMANGET
  - Antonin GARRET
  - Erwan LE FLEM
  - Pierre LE LURON
  - Alexis LE MASLE
  - Mickaël LEBRETON
  - Fahim MERZOUK
* Alexis LE MASLE (internship during 2018 summer)
* Master 1's team of 2018-2019 :
  - Valentin PETIT
  - Julien ROYON CHALENDARD
  - Cyril HAMON
  - Paul SAFFRAY
  - Michaël PICARD
  - Malo POLES
  - Luis THOMAS
  - Alexis BONNET
* Paul SAFFRAY (internship during 2019 summer)

# Notes on this fork

## Requirements

- [python-mysql](https://github.com/PyMySQL/mysqlclient-python)

  We suggest to install with your package manager instead of `pip`.
  For more info, please check the notes from its [github
  repository](https://github.com/PyMySQL/mysqlclient-python):

  > This project adds Python 3 support and bug fixes. I hope this fork is
  > merged back to MySQLdb1 like distribute was merged back to setuptools.

  and this [stackoverflow
  question](https://stackoverflow.com/questions/42357853/mysql-python-pip-install-error)

- [sphinx](https://www.sphinx-doc.org/en/master/)

  Check sphinx extensions used in the [configuration
file](https://github.com/garandria/ProjetIrma/blob/master/Documentation/conf.py#L39)

- [docker](https://www.docker.com/)
