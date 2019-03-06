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

We first thought that the randconfig algorithm would prioritize the option we specifie and will, if needed, set `CONFIG_EXPERT` to Y even if it was randomly not set before. To sum up we assumed that the randconfig algorithm would "satisfy" a direct dependance if needed. After further test we realise it was not the case and so, when `CONFIG_SLOB` was actually set at Y, it was by luck and not because we specified it. The solution is obvioulsy to set `CONFIG_EXPERT` at Y in the config file.

This finding led us to build a test-case for every option in the config file.

### CONFIG_CC_OPTIMIZE_FOR_SIZE option
The [`CONFIG_CC_OPTIMIZE_FOR_SIZE` option](https://gcc.gnu.org/onlinedocs/gcc/Optimize-Options.html) is an option that will change the optimization level of GCC from "-O2" to "-Os". This option try to maintain as much optimization as an "-O2" compilation but disable some of the flag that are [known to increase code size](https://gcc.gnu.org/onlinedocs/gcc/Optimize-Options.html). The compiler will be tune for code size rather than execution speed. As we are,right now, looking for the smaller kernel possible, we want this option to be set to Y.

Since this option does not have any dependance we can use it to validate our test-case. we neer found this options to be at a value we didn't expect it to be.

### CONFIG_X86_NEED_RELOCS options
The [`CONFIG_X86_NEED_RELOCS` option](https://cateee.net/lkddb/web-lkddb/X86_NEED_RELOCS.html) is a "blind" option. What it means is that it's not possible to select this option directly. This option is use "propagate" options and make the Kconfig file more readable. 

i.e : 

config OPT1:
* depends on :
* OPT2 || (OPT3 && OPT4)

config OPT5:
* depend on :
* OPT1   //(<=> OPT2||(OPT3 && OPT4))

In this case, the option `CONFIG_X86_NEED_RELOCS` is use to propagate the options [`CONFIG_RANDOMIZE_BASE`](https://cateee.net/lkddb/web-lkddb/RANDOMIZE_BASE.html) `|| ( `[`CONFIG_X86_32`](https://cateee.net/lkddb/web-lkddb/X86_32.html)` &&`[`CONFIG_RELOCATABLE`](https://cateee.net/lkddb/web-lkddb/RELOCATABLE.html) `)`
wich are options that are used to randomize the physical address where the kernel is decompressed and the virtual address where the kernel is mapped. This is a security feature that increase the size of the kernel binary [by 10%.](https://github.com/torvalds/linux/blob/master/arch/x86/Kconfig) That why we want this option set to N.

The test of this option does not make sense because of the way the randconfig and Kconfig algorithm are implemented. However, as user, we would expect this option to be settable and to propagate the set value to the dependances.

###  Kasan option and conditional
[`KASan or Kernel Address SANitizer`](https://cateee.net/lkddb/web-lkddb/KASAN.html) is a runtime memory debugger design to find out-of-bound access and use-after-free bugs. It consumes about 1/8 of the available memory and slowdown the performances by a factor 3. In our case we do not want this option to be activated in our kernel config file.

However this option is interesting because it introduces a new type of options, the conditional option. A conditional option is a boolean option that enable another set of options.

In our case the conditional is [`HAVE_ARCH_KASAN`](https://cateee.net/lkddb/web-lkddb/HAVE_ARCH_KASAN.html) that enable Kasan's options if set to true. However our tests shows that, like a 'blind option', this conditional can't be set directly in the .config file. Wich means that if we set options that depends on [`HAVE_ARCH_KASAN`] directly in the .config file we can't be sure that they will remain set after the randconfig algorithm, because we cannot set `HAVE_ARCH_KASAN` in the .config file in the first place.

We conducted further test using another conditional option [`USB_SERIAL`](https://github.com/torvalds/linux/blob/v4.20/drivers/usb/serial/Kconfig) and we observed the same behavior. 

The main difference between `blind options` and `conditional options` is that `blind options` are used to propagate options in Kconfig files while `conditional options` are used to enable access to more options.

### Conclusion

To conclude we can say that creating .config file using randconfig while pre-setting options seems to lead to behavior that are not predictable. It also seems that thoses behavior are more or less random on their own, wich means that we can't assume anything when generating .config this way. And we should check every .config file before using them. One workaround that limit thoses behavior is to explicitly set every options and dependances manualy, but even with this technique, we can't assume that they will remains set after the randconfig algorithm is use.