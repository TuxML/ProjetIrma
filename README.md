# Welcome to TuxML

TuxML stands for Tux and Machine Learning (ML), Machine Learning applied to the options of Linux kernel configurations. The Linux kernel has near 14 000 options allowing to provide an infinity of different Linux kernels. To do that, we are harvesting several thousand of compilations data gained by the mass compilation of Linux kernels to be able to "predict" the characteristics of a kernel from its configuration.


### Easily contributing

Requirement:
`Python3` and `Docker` are needed to run `MLfood.py` and the TuxML project which is on the Docker Image.
Do not forget to start the docker service. (Exemple: `sudo service docker start`)

```
mkdir -p ~/TuxML ; cd ~/TuxML ; wget https://github.com/TuxML/ProjetIrma/releases/download/v0.8/MLfood.py ; python3 MLfood.py 100 --dev
```
I will create a folder "TuxML" in your home.
Copy this command and run it in a terminal, you can modify the 100 to an other number.

Once you ran this command once, you can run `MLfood.py` again with the normal way.


## Summary of our wiki

1. [Introduction](https://github.com/TuxML/ProjetIrma/wiki)
2. [Installation](https://github.com/TuxML/ProjetIrma/wiki/Installation)
3. [Quick Start](https://github.com/TuxML/ProjetIrma/wiki/Quick-Start)
4. [How To (Main questions)](https://github.com/TuxML/ProjetIrma/wiki/How-To-(Main-questions))
5. [Details on main scripts](https://github.com/TuxML/ProjetIrma/wiki/Details-on-main-scripts/)

Plese check our [wiki](https://github.com/TuxML/ProjetIrma/wiki)
