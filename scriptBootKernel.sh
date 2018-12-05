#!/bin/bash
 
TOP=$HOME/kdev
cp -rf /TuxML/linux-4.13.3/ $TOP/linux

#Configure Linux using simple defconfig and kvm options
cd $TOP/linux
make O=$TOP/build/linux-x86-basic x86_64_defconfig
make O=$TOP/build/linux-x86-basic kvmconfig

#Build Linux
make O=$TOP/build/linux-x86-basic -j2

#Boot with Qemu
cd $TOP
qemu-system-x86_64 \
  -kernel build/linux-x86-basic/arch/x86_64/boot/bzImage \
  -initrd build/initramfs-busybox-x86.cpio.gz \
  -nographic -append "console=ttyS0" >> log.txt &

# Watch if Boot works or not
cd ~/..
./watchBootKernel.sh
