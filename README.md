# TuxML: Machine Learning and Linux Kernel


The goal of TuxML is to predict properties of Linux Kernel configurations (e.g., does the kernel compile? what's its size? does it boot?). 
The Linux Kernel provides nearly 15000 configuration options: there is an infinity of different kernels. 
As we cannot compile, measure, and observe all combinations of options (aka configurations), we're trying to learn Linux kernel properties out of samples of configurations.
You can easily loan your machine and contribute if you want, just copy and paste the line below!

<img align="right" width="100" height="100" src="miscellaneous/informations/tuxml_logo_small.png" alt="TuxML's Logo"/>

The goal of the TuxML team is to develop tools, mainly based on Docker and Python, to massively compile and gather data about thousand of kernel configurations.
The TuxML name comes from the combination of [Tux](https://en.wikipedia.org/wiki/Tux_(mascot)), the mascot of the Linux Kernel, and ML for statistical Machine Learning.

## I want to help by compiling some Linux kernels!

Requirements : `Python3` and `Docker` are needed (do not forget to start the docker service usually with `sudo service docker start`).

```bash
mkdir -p ~/TuxML ; cd ~/TuxML ; wget https://github.com/TuxML/ProjetIrma/releases/download/v2.0/kernel_generator.py ; python3 kernel_generator.py 10
```

Copy this command and run it in a terminal. It will create a folder "TuxML" in your homedir and send compilation results to our database.
You can modify the 10 parameter to any other number (it's the number of kernels your machine will compile).
The python script gives you some other options that you can use, see [this page for more](https://github.com/TuxML/ProjetIrma/wiki/User_documentation#python-script-entry-point--kernel_generatorpy).

For a more up-to-date version of TUXML, please consider the **dev branch**, i.e.:
`wget https://raw.githubusercontent.com/TuxML/ProjetIrma/dev/kernel_generator.py`

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
