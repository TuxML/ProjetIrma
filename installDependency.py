#!/bin/python
import platform
import subprocess
import shutil

def packageManagerIs(packageManagerName):
    return shutil.which(packageManagerName)

def installDependency():
    if (packageManagerIs("apt-get")):
        print("apt-get found")
    elif (packageManagerIs("pacman")):
        returnCode = subprocess.run(["pacman", "-Syu"]).returncode
        if (returnCode == 0):
            completedProcess = subprocess.run(["pacman", "-S", "gcc", "make", "binutils", "util-linux", "kmod", "e2fsprogs", "jfsutils", "reiserfsprogs", "xfsprogs", "squashfs-tools",
            "btrfs-progs", "pcmciautils", "quota-tools", "ppp", "isdn4k-utils", "nfs-utils", "procps-ng", "oprofile", "grub", "iptables", "openssl", "bc"])
    else:
        returnCode = 1
    return completedProcess.returncode

installDependency()
