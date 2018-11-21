#!/bin/bash

# Installing necessary package
apt -y install ncurses-dev build-essential libssl-dev libelf-dev cpio wget

# Prepare a working space for kernel development
cd $HOME
mkdir kdev
TOP=$HOME/kdev

# Download source code
wget http://busybox.net/downloads/busybox-1.24.2.tar.bz2
tar xvf busybox-1.24.2.tar.bz2
rm busybox-1.24.2.tar.bz2
mv -f busybox-1.24.2/ kdev/

# Configure busybox
cd $TOP/busybox-1.24.2
mkdir -p $TOP/build/busybox-x86
make O=$TOP/build/busybox-x86 defconfig
# make O=$TOP/build/busybox-x86 menuconfig
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

cp /init $TOP/build/initramfs/busybox-x86
chmod +x init
# Generate initramfs
find . -print0 | cpio --null -ov --format=newc | gzip -9 > $TOP/build/initramfs-busybox-x86.cpio.gz