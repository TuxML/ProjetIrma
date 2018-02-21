#!/bin/python
<<<<<<< HEAD

#   Copyright 2018 TuxML Team
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

=======
>>>>>>> 48a1dddd0a0c8d66d7b16ba305d3ef3a8c338f1a
import subprocess
import shutil
import tuxml_common as tcom
import tuxml_settings as tset


# author : LE FLEM Erwan
#
# Find the missing packages (ArchLinux distribution)
#
# return value :
#   -1 package not found
#    0 installation OK
def build_dependencies_arch(missing_files, missing_packages):
    if tset.VERBOSE > 0:
        tcom.pprint(3, "Arch based distro")

    return 0


# author : LEBRETON Mickael
#
# Find the missing packages (Debian distribution)
#
# return value :
#   -1 package not found
#    0 installation OK
def build_dependencies_debian(missing_files, missing_packages):
    if tset.VERBOSE > 0:
        tcom.pprint(3, "Debian based distro")

    cmd_search  = "apt-file search {}" # cherche dans quel paquet est le fichier
    cmd_check   = "dpkg-query -l | grep {}" # vérifie si le paquet est présent sur le système

    if tset.VERBOSE > 0 and len(missing_files) > 0:
        tcom.pprint(3, "Those files are missing :")

    for mf in missing_files:
        if tset.VERBOSE > 0:
            print(" " * 3 + mf)

        try:
            output = subprocess.check_output([cmd_search.format(mf)], shell=True, universal_newlines=True)
        except subprocess.CalledProcessError:
            tcom.pprint(1, "Unable to find the missing package(s)")
            return -1

        # Sometimes the  output gives  several packages. The  program takes  the
        # first one and check if the package is already installed. If not, tuxml
        # installs it. Else it installs the next one
        lines = output.splitlines()
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

        # if tuxml reaches the end of the packages list without installing any package
        # it means that there is a problem with mf, so it returns an error
        if i > len(lines) and status == 0:
            tcom.pprint(1, "Unable to find the missing package(s)")
            return -1

    tcom.pprint(0, "Dependencies built")
    return 0


# author :
#
# Find the missing packages (RedHat distribution)
#
# return value :
#   -1 package not found
#    0 installation OK
def build_dependencies_redhat(missing_files, missing_packages):
    if tset.VERBOSE > 0:
        tcom.pprint(3, "RedHat based distro")

    return 0


# authors : LE FLEM Erwan, MERZOUK Fahim
#
# Install packages of required dependencies to compile the kernel
#
# return
#   -1 Unable to install some packages
#    0 succes
def install_default_dependencies():
    # Install packages common to all distro
    tcom.pprint(2, "Installing default dependencies")

    common_pkgs = ["gcc", "make", "binutils", "util-linux", "kmod", "e2fsprogs", "jfsutils", "xfsprogs", "btrfs-progs", "pcmciautils", "ppp", "grub","iptables","openssl", "bc"]

    # Now installation of packages with name that vary amongs distributions
    # TODO ajouter les paquets python3-pip, mysql-client?, libmariadbclient-dev, mysql-server?
    debian_specific = ["reiserfsprogs" , "squashfs-tools", "quotatool", "nfs-kernel-server", "procps", "mcelog", "libcrypto++6", "apt-utils"]
    arch_specific   = ["reiserfsprogs" , "squashfs-tools", "quota-tools", "isdn4k-utils", "nfs-utils", "procps-ng", "oprofile"]
    redHat_specific = ["reiserfs-utils", "squashfs-tools", "quotatool", "isdn4k-utils", "nfs-utils", "procps-ng", "oprofile", "mcelog"]
    gentoo_specific = ["reiserfsprogs" , "squashfs-tools", "quotatool", "nfs-utils", "procps", "mcelog", "oprofile"]
    suse_specific   = ["reiserfs", "quota", "nfs-client" , "procps"]

    specific_pkgs = {
        "apt-get" : debian_specific,
        "pacman" : arch_specific,
        "dnf":redHat_specific,
        "yum":redHat_specific,
        "emerge":gentoo_specific,
        "zypper":suse_specific
    }

    if tcom.install_packages(common_pkgs + specific_pkgs[tset.PKG_MANAGER]) != 0:
        return -1
    else:
        return 0
