#!/bin/python
import subprocess
import shutil
import tuxml_common as tcom
import tuxml_settings as tset


# author : LE FLEM Erwan
#
# [build_dependencies_arch description]
#
# return value :
#   -1 package not found
#    0 installation OK
def build_dependencies_arch(missing_files, missing_packages):
    if tset.VERBOSE:
        tcom.pprint(3, "Arch based distro")

    return 0


# author : LEBRETON Mickael
#
# [build_dependencies_debian description]
#
# return value :
#   -1 package not found
#    0 installation OK
def build_dependencies_debian(missing_files):
    if tset.VERBOSE:
        tcom.pprint(3, "Debian based distro")

    cmd_search  = "apt-file search {}" # cherche dans quel paquet est le fichier
    cmd_check   = "dpkg-query -l | grep {}" # vérifie si le paquet est présent sur le système

    if tset.VERBOSE and len(missing_files) > 0:
        tcom.pprint(3, "Those files are missing :")

    missing_packages = []
    for mf in missing_files:
        if tset.VERBOSE:
            print(" " * 3 + mf)

        output = subprocess.check_output([cmd_search.format(mf)], shell=True)

        # Sometimes the  output gives  several packages. The  program takes  the
        # first one and check if the package is already installed. If not, tuxml
        # installs it else it installs the next one
        lines = output.decode("utf-8").splitlines()
        i = 0
        status = 0
        while i < len(lines) and status == 0:
            package = lines[i].split(":")[0]
            # 0: package already installed
            # 1: package not installed
            status = subprocess.call([cmd_check.format(package)], stdout=tset.OUTPUT, stderr=tset.OUTPUT, shell=True)
            if status == 1:
                missing_packages.append(package)
            i += 1

    return missing_packages


# author :
#
# [build_dependencies_redhat description]
#
# return value :
#   -1 package not found
#    0 installation OK
def build_dependencies_redhat(missing_files, missing_packages):
    if tset.VERBOSE:
        tcom.pprint(3, "RedHat based distro")

    return 0


# authors : LE FLEM Erwan, MERZOUK Fahim
#
# Install packages of required dependencies to compile the kernel
#
# return
#   -2 No packages manager found
#   -1 Unable to install some packages
#    0 succes
def install_default_dependencies():
    pkg_manager = tcom.get_package_manager();
    if pkg_manager == None:
        return -2

    tcom.update_system(pkg_manager)

    # Install packages common to all distro
    tcom.pprint(2, "Installing default dependencies")

    common_pkgs = ["gcc", "make", "binutils", "util-linux", "kmod", "e2fsprogs", "jfsutils", "xfsprogs", "btrfs-progs", "pcmciautils", "ppp", "grub","iptables","openssl", "bc"]

    if tcom.install_packages(pkg_manager, common_pkgs) != 0:
        return -1

    # Now installation of packages with name that vary amongs distributions
    # TODO ajouter les paquets python3-pip, mysql-client?, libmariadbclient-dev, mysql-server? pour les autres distib
    debian_specific = ["reiserfsprogs" , "squashfs-tools", "quotatool", "nfs-kernel-server", "procps", "mcelog", "libcrypto++6", "apt-utils", "python3-pip", "mysql-client", "mysql-server", "libmariadbclient-dev"]
    arch_specific   = ["reiserfsprogs" , "squashfs-tools", "quota-tools", "isdn4k-utils", "nfs-utils", "procps-ng", "oprofile"]
    redHat_specific = ["reiserfs-utils", "squashfs-tools", "quotatool", "isdn4k-utils", "nfs-utils", "procps-ng", "oprofile", "mcelog"]
    gentoo_specific = ["reiserfsprogs" , "squashfs-tools", "quotatool", "nfs-utils", "procps", "mcelog", "oprofile"]
    suse_specific   = ["reiserfs", "quota", "nfs-client" , "procps"]

    # TODO pip3 install mysqlclient

    specific_pkgs = {
        "apt-get" : debian_specific,
        "pacman" : arch_specific,
        "dnf":redHat_specific,
        "yum":redHat_specific,
        "emerge":gentoo_specific,
        "zypper":suse_specific
    }

    if tcom.install_packages(pkg_manager, specific_pkgs[pkg_manager]) != 0:
        return -1
    else:
        return 0
