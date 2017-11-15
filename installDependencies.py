#!/bin/python
import subprocess
import shutil
import tuxml_common


# authors : LE FLEM Erwan, MERZOUK Fahim
# Install packages of required dependencies to compile the kernel
# return zero on sucess, - 2 if no packages manager is found on error, other values for installation error.
def installDependency():
    pkg_manager = get_package_manager();
    if pkg_manager == None:
        return -2

    update_package_manager()
    #Installation of package with name common for all distributions.
    common_pkg = ["gcc", "make", "binutils", "util-linux", "kmod", "e2fsprogs", "jfsutils", "xfsprogs", "btrfs-progs", "pcmciautils", "ppp", "grub","iptables","openssl", "bc"]
    print("[*] Installation...")
    returnCode = installPackages(common_pkg)

    if (returnCode != 0):
        print("[-] Error while installing common packages")
        return returnCode

    # Now installation of packages with name that vary amongs distributions
    debian_specific = ["reiserfsprogs", "squashfs","quotatool", "nfs-kernel-server","procps", "mcelog", "libcrypto++6"
    ,"apt-utils"]

    arch_specific = ["reiserfsprogs", "squashfs-tools","quota-tools", "isdn4k-utils", "nfs-utils", "procps-ng", "oprofile"]

    redHat_specific =  ["reiserfs-utils", "squashfs-tools", "quotatool","isdn4k-utils", "nfs-utils", "procps-ng", "oprofile", "mcelog"]

    gentoo_specific =  ["reiserfsprogs", "squashfs-tools", "quotatool", "nfs-utils", "procps", "mcelog", "oprofile"]

    suse_specific =  ["reiserfs", "quota", "nfs-client", "procps"]

    packageSpecific = {"apt-get" : debian_specific, "pacman" : arch_specific, "dnf":redHat_specific, "yum":redHat_specific, "emerge":gentoo_specific, "zypper":suse_specific}
    returnCode = installPackages(packageSpecific[pkg_manager])

    if (returnCode != 0):
        print("[-] Error while installing distrib specific packages")
        return errorCode
