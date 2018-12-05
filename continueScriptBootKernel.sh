#!/bin/bash

cd $HOME/kdev
qemu-system-x86_64 \
  -kernel build/linux-x86-basic/arch/x86_64/boot/bzImage \
  -initrd build/initramfs-busybox-x86.cpio.gz \
  -nographic -append "console=ttyS0" >> log.txt &

