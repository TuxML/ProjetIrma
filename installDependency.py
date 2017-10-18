#!/bin/python
import platform
import subprocess
import shutil

def packageManagerIs(packageManagerName):
    return shutil.which(packageManagerName)

def installDependency():
    if (packageManagerIs("apt-get")):
        print("apt-get found")
    if (packageManagerIs("pacman")):
        returnCode = subprocess.run(["pacman", "-Si", "gcc", "make", "binutils", "util-linux", "kmod", "e2fsprogs", "jfsutils", "reiserfsprogs", "xfsprogs", "squashfs-tools",
        "btrfs-progs", "pcmciautils", "quota-tools", "ppp", "isdn4k-utils", "nfs-utils", "procps-ng", "oprofile", "grub", "iptables", "openssl", "bc"])

        # print("gestionnaire non géré found")
        # returnCode = 1
    return returnCode

installDependency()
