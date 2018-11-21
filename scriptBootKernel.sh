#!/bin/bash
 
# Install required build tools on host machine ubuntu
apt update
apt install -y ncurses-dev build-essential libssl-dev libelf-dev git qemu

# Prepare a working space for kernel development
cd $HOME
mkdir kdev
TOP=$HOME/kdev

# Download source code
wget http://busybox.net/downloads/busybox-1.24.2.tar.bz2
tar xvf busybox-1.24.2.tar.bz2
rm busybox-1.24.2.tar.bz2
mv -f busybox-1.24.2/ kdev/
cp -rf /TuxML/linux-4.13.3/ $TOP/linux

# Configure busybox
cd $TOP/busybox-1.24.2
mkdir -p $TOP/build/busybox-x86
make O=$TOP/build/busybox-x86 defconfig
#make O=$TOP/build/busybox-x86 menuconfig
echo "CONFIG_STATIC=y" >> $TOP/build/busybox-x86/.config

# Build and install busybox
cd $TOP/build/busybox-x86
make -j2
make install

# Create minimal filesystem
mkdir -p $TOP/build/initramfs/busybox-x86
cd $TOP/build/initramfs/busybox-x86
mkdir -pv {bin,sbin,etc,proc,sys,usr/{bin,sbin}}
cp -av $TOP/build/busybox-x86/_install/* .

cp $HOME/../init $TOP/build/initramfs/busybox-x86
chmod +x init
# Generate initramfs
find . -print0 \
   | cpio --null -ov --format=newc \
   | gzip -9 > $TOP/build/initramfs-busybox-x86.cpio.gz

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
