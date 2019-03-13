# HOW TO


### Install Kconfiglib


`pip[3] install kconfiglib`

---
### Patch Kernel Makefile

Before used the functionnality of Kconfiglib on a kernel Linux, you need to patch the Makefile in the folder "kernel_name/scripts/kconfig"

To realize this : 

1. `git clone https://github.com/ulfalizer/Kconfiglib.git`
2. Download a Linux kernel
3. In the kernel directory : 

`patch -p1 < Kconfiglib/makefile.patch`

---

### Usage

 Always in the kernel directory, you can run, for instance, the file print_tree.py (which print the options in kconfig file) like this : 

`make [ARCH=arch] scriptconfig SCRIPT=Kconfiglib/examples/print_tree.py`

