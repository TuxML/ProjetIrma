#!/bin/python
import platform
import subprocess
import shutil

def packageManagerIs(packageManagerName):
    return shutil.which(packageManagerName)

def getActualManager(manager1, manager2):
    if (packageManagerIs(manager1)):
        return manager1
    else
        return manager2


def installDependency():
    if (packageManagerIs("aptitude") | packageManagerIs("apt-get")):
        packageManagerName = getActualManager("aptitude", "apt-get")
        subprocess.run([packageManagerName, "update"])
        returnCode = subprocess.run([packageManagerName, "upgrade"]).returncode
        if(returnCode == 0):
            completedProcess = subprocess.run([packageManagerName, "install" ,"gcc","make",
            "binutils","util-linux","kmod","e2fsprogs","jfsutils",
            "reiserfsprogs", "xfsprogs", "squashfs" , "btrfs-progs",
            "pcmiautils","quotatool", "ppp", "nfs-kernel-server",
            "procps","grub", "mcelog", "iptables", "openssl", "libcrypto++6","bc"])
    elif (packageManagerIs("pacman")):
        returnCode = subprocess.run(["pacman", "-Syu"]).returncode
        if (returnCode == 0):
            completedProcess = subprocess.run(["pacman", "-S", "gcc", "make", "binutils", "util-linux", "kmod", "e2fsprogs", "jfsutils", "reiserfsprogs", "xfsprogs", "squashfs-tools",
            "btrfs-progs", "pcmciautils", "quota-tools", "ppp", "isdn4k-utils", "nfs-utils", "procps-ng", "oprofile", "grub", "iptables", "openssl", "bc"])
    elif (packageManagerIs("dnf") | packageManagerIs("yum")):
        packageManagerName = getActualManager("dnf", "yum")
        returnCode = subprocess.run([packageManagerName, "upgrade"]).returncode
        if (returnCode == 0):
            completedProcess = subprocess.run([packageManagerName, "install", "gcc", "make", "binutils", "util-linux", "kmod", "e2fsprogs", "jfsutils", "reiserfs-utils", "xfsprogs", "squashfs-tools",
            "btrfs-progs", "pcmciautils", "quotatool", "ppp", "isdn4k-utils", "nfs-utils", "procps-ng", "oprofile", "grub", "mcelog", "iptables", "openssl", "bc"])
    else:
        returnCode = 1
    return completedProcess.returncode

installDependency()
