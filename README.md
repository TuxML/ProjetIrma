# TuxML: Machine Learning and Linux Kernel

The goal of TuxML is to predict properties of Linux Kernel configurations (e.g., does the kernel compile? what's its size? does it boot?). 
The Linux Kernel provides near 15000 configuration options: there is an infinity of different kernels. 
As we cannot compile, measure, and observe all combinations of options (aka configurations), we're trying to learn Linux kernel properties out of a sample of configurations. 
You can easily loan your machine and contribute if you want, just copy and paste the line below! <img align="right" width="100" height="100" src="https://raw.githubusercontent.com/TuxML/ProjetIrma/master/informations/tuxml_logo_small.png" /> 

The TuxML* project is developping tools, mainly based on Docker and Python, to massively compile and gather data about thousand of configuration kernels. *([Tux](https://en.wikipedia.org/wiki/Tux_(mascot)) is the mascotte of the Linux Kernel while ML stands for statistical machine learning) 

### I want to compile some Linux kernels! 

Requirement: `Python3` and `Docker` are needed (do not forget to start the docker service usually with `sudo service docker start`)

```
mkdir -p ~/TuxML ; cd ~/TuxML ; wget https://github.com/TuxML/ProjetIrma/releases/download/v1.1/kernel_generator.py ; python3 kernel_generator.py 10 --dev
```

Copy this command and run it in a terminal. It will create a folder "TuxML" in your home and sent compilation results to our database.
You can modify the 10 to an other number (it's the number of kernels your machine will compile).

# Summary of our wiki

1. [Introduction](https://github.com/TuxML/ProjetIrma/wiki)
2. [Installation](https://github.com/TuxML/ProjetIrma/wiki/Installation)
3. [Quick Start](https://github.com/TuxML/ProjetIrma/wiki/Quick-Start)
4. [How To (Main questions)](https://github.com/TuxML/ProjetIrma/wiki/How-To-(Main-questions))
5. [Details on main scripts](https://github.com/TuxML/ProjetIrma/wiki/Details-on-main-scripts/)

Plese check our [wiki](https://github.com/TuxML/ProjetIrma/wiki)

# Contributors 

 * Mathieu Acher (Univ Rennes, Inria, CNRS, IRISA), scientific leader  
 * Alexis LE MASLE (University of Rennes 1), main developer 
 * [DiverSE team (Inria/IRISA research team)](http://www.diverse-team.fr/)
 * [ANR VaryVary project](https://varyvary.github.io/) 

    Master 2017 - 2018

 * Corentin CHÉDOTAL
 * Gwendal DIDOT 
 * Dorian DUMANGET 
 * Antonin GARRET
 * Erwan LE FLEM
 * Pierre LE LURON 
 * Alexis LE MASLE 
 * Mickaël LEBRETON
 * Fahim MERZOUK

    Master 2018 - 2019  

 * Valentin PETIT
 * Julien ROYON CHALENDARD
 * Cyril HAMON
 * Paul SAFFRAY
 * Michaël PICARD
 * Malo POLES
 * Luis THOMAS
 * Alexis BONNET

