#!/bin/python
import platform
import subprocess
import shutil

def packageManagerIs(packageManagerName):
    return shutil.which(packageManagerName)

def installDependency():
    if (packageManagerIs("aptitude")):
        subprocess.run(["aptitude", "update"])
        returnCode = subprocess.run(["aptitude", "upgrade"]).returncode
        if(returnCode == 0):
            completedProcess = subprocess.run(["aptitude" , "install" ,"gcc","make",
            "binutils","util-linux","kmod","e2fsprogs","jfsutils",
            "reiserfsprogs", "xfsprogs", "squashfs" , "btrfs-progs",
            "pcmiautils","quotatool", "ppp", "nfs-kernel-server",
            "procps","grub", "mcelog", "iptables", "openssl", "libcrypto++6","bc"])
    elif (packageManagerIs("apt-get")):
        subprocess.run(["apt-get", "update"])
        returnCode = subprocess.run(["apt-get", "upgrade"]).returncode
        if(returnCode == 0):
            completedProcess = subprocess.run(["apt-get" , "install" ,"gcc","make",
            "binutils","util-linux","kmod","e2fsprogs","jfsutils",
            "reiserfsprogs", "xfsprogs", "squashfs" , "btrfs-progs",
            "pcmiautils","quotatool", "ppp", "nfs-kernel-server",
            "procps","grub", "mcelog", "iptables", "openssl", "libcrypto++6","bc"])
    elif (packageManagerIs("pacman")):
        returnCode = subprocess.run(["pacman", "-Syu"]).returncode
        if (returnCode == 0):
            completedProcess = subprocess.run(["pacman", "-S", "gcc", "make", "binutils", "util-linux", "kmod", "e2fsprogs", "jfsutils", "reiserfsprogs", "xfsprogs", "squashfs-tools",
            "btrfs-progs", "pcmciautils", "quota-tools", "ppp", "isdn4k-utils", "nfs-utils", "procps-ng", "oprofile", "grub", "iptables", "openssl", "bc"])
    else:
        returnCode = 1
    return completedProcess.returncode

installDependency()
