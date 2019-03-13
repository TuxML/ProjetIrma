Work in progress

# The usage of ranconfig in TuxML project

## Introduction to TuxML

The TuxML project has two goals :

* Help the developpers and contributors of the Linux kernel to understand, document and maintain the Linux kernel options in a better way.
* Help the users to choose their configuration without any knowledge of the kernel options.

To do so we generate random kernel options config file and we compile the kernel using thoses options in a specific environnement. During the whole process, data are collected to feed a machine learning algorithm. The algorithm is then able to answer "high level" questions such as : "What does this option involve in the kernel size ?", "What will happend on the boot time if I use this options ?"

To generate random kernel options config files we use randonfig. Randconfig is part of Kconfig process. The purpose of randoconfg is to generate a .config file with all the options filled randomly.

## Options specialization

To narrow down the possibilities (i.e X86 arch only) , we want to specifie some options and apply the randomization to the others. To do so we use this line to generate the .config file :     `KCONFIG_ALLCONFIG=" + file + " make randconfig` where `file` contain the options we want to specialize.

## Test

We run our tests with a python [script](https://github.com/TuxML/ProjetIrma/blob/dev/special-config/kconfig_checker.py) that run `KCONFIG_ALLCONFIG=" + file + " make randconfig` and then check if the options specified in `file` are set at the same value in the .config file. After testing we found out that one option, `CONFIG_SLOB`, wasn't set at the right value in 25% of the .config files.

### CONFIG_SLOB option

The [`CONFIG_SLOB` option](https://cateee.net/lkddb/web-lkddb/SLOB.html) when enable replace the SLUB allocator (>=2.6.23) with a simpler memory allocator that is more efficient on small system with small amount of memory. The drawback is the poor scalability of the SLOB allocator.

Since the SLOB allocator has a great impact on the kernel size we want it to be set at Y. For kernel prior version 2.6.23 this will work without problem.However after this version the `CONFIG_SLOB` option has a dependance on [`CONFIG_EXPERT` option](https://cateee.net/lkddb/web-lkddb/EXPERT.html).
This option allows certains base kernel options or settings to be tweaked.

We first thought that the randconfig algorithm would prioritize the option we specifie and will, if needed, set `CONFIG_EXPERT` to Y even if it was randomly not set before. To sum up we assumed that the randconfig algorithm would "satisfy" a direct dependancie if needed. After further test we realise it was not the case and so, when `CONFIG_SLOB` was actually set at Y, it was by luck and not because we specified it.