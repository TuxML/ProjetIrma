#!/bin/bash

# Install required build tools on host machine ubuntu
eval $echo apt install ncurses-dev build-essential libssl-dev libelf-dev
eval $echo apt install git
eval $echo apt install qemu

# Prepare a working space for kernel development
eval $echo cd $HOME
eval $echo mkdir kdev
eval $echo TOP=$HOME/kdev

# Download source code
eval $echo wget http://busybox.net/downloads/busybox-1.24.2.tar.bz2
eval $echo tar xvf busybox-1.24.2.tar.bz2
eval $echo rm busybox-1.24.2.tar.bz2
eval $echo mv -f busybox-1.24.2/ kdev/
eval $echo cp -rf /TuxML/linux-4.13.3/ ~/kdev/linux

# Configure busybox
eval $echo cd $TOP/busybox-1.24.2
eval $echo mkdir -p $TOP/build/busybox-x86
eval $echo make O=$TOP/build/busybox-x86 defconfig
eval $echo make O=$TOP/build/busybox-x86 menuconfig

# Build and install busybox
eval $echo cd $TOP/build/busybox-x86
eval $echo make -j2
eval $echo make install

# Create minimal filesystem
eval $echo mkdir -p $TOP/build/initramfs/busybox-x86
eval $echo cd $TOP/build/initramfs/busybox-x86
eval $echo mkdir -pv {bin,sbin,etc,proc,sys,usr/{bin,sbin}}
eval $echo cp -av $TOP/build/busybox-x86/_install/* .

# Create simple init script
eval $echo cat >init<<EOF

#!/bin/sh 

#code

mount -t proc none /proc

mount -t sysfs none /sys

echo -e "\nBoot took $(cut -d' ' -f1 /proc/uptime) seconds\n"

exec /bin/sh"

EOF

eval $echo chmod +x init

# Generate initramfs
eval $echo find . -print0 \
   | cpio --null -ov --format=newc \
   | gzip -9 > $TOP/build/initramfs-busybox-x86.cpio.gz

# Configure Linux using simple defconfig and kvm options
eval $echo cd $TOP/linux
eval $echo make O=$TOP/build/linux-x86-basic x86_64_defconfig
eval $echo make O=$TOP/build/linux-x86-basic kvmconfig

# Build Linux
eval $echo make O=$TOP/build/linux-x86-basic -j2

# Boot with Qemu
eval $echo cd $TOP
eval $echo qemu-system-x86_64 \
  -kernel build/linux-x86-basic/arch/x86_64/boot/bzImage \
  -initrd build/initramfs-busybox-x86.cpio.gz \
  -nographic -append "console=ttyS0"
