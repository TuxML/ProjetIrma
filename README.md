# TuxML: Machine Learning and Linux Kernel


The goal of TuxML is to predict properties of Linux Kernel configurations (e.g., does the kernel compile? what's its size? does it boot?). 
The Linux Kernel provides near 15000 configuration options: there is an infinity of different kernels. 
As we cannot compile, measure, and observe all combinations of options (aka configurations), we're trying to learn Linux kernel properties out of a sample of configurations. 
You can easily loan your machine and contribute if you want, just copy and paste the line below!

<img align="right" width="100" height="100" src="miscellaneous/informations/tuxml_logo_small.png" alt="TuxML's Logo"/>
The TuxML's goal is to develop tools, mainly based on Docker and Python, to massively compile and gather data about thousand of configuration kernels.
TuxML name come from the combination of [Tux](https://en.wikipedia.org/wiki/Tux_(mascot)), the mascot of the Linux Kernel, and ML for statistical machine learning.

## I want to help by compiling some Linux kernels!

Requirement: `Python3` and `Docker` are needed (do not forget to start the docker service usually with `sudo service docker start`).

```bash
mkdir -p ~/TuxML ; cd ~/TuxML ; wget https://github.com/TuxML/ProjetIrma/releases/download/v1.1/kernel_generator.py ; python3 kernel_generator.py 10
```

Copy this command and run it in a terminal. It will create a folder "TuxML" in your home and sent compilation results to our database.
You can modify the 10 to an other number (it's the number of kernels your machine will compile).
The python script propose other option that you can use, see [this page for more](https://github.com/TuxML/ProjetIrma/wiki/User_documentation#python-script-entry-point--kernel_generatorpy).

## I want to know more about the project!

Please check our [wiki](https://github.com/TuxML/ProjetIrma/wiki).

## Contributors' list

* Mathieu Acher (University Rennes 1, INRIA, CNRS, IRISA), scientific leader
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
