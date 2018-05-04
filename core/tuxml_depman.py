#!/usr/bin/python3

# -*- coding: utf-8 -*-

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

## @file tuxml_depman.py
#  @author LE FLEM Erwan
#  @author LEBRETON Mickaël
#  @author MERZOUK Fahim
#  @copyright Apache License 2.0
#  @brief Packages and missing packages dependencies handler.


import subprocess
import tuxml_common as tcom
import tuxml_settings as tset
import tuxml_depLog as tdepl


## Dependencies logger
tdepLogger = tdepl


## @author  LE FLEM Erwan
#  @author  LEBRETON Mickael
#  @author  MERZOUK Fahim
#
#  @brief   Find the missing packages thanks to the missing files list
#  @details Find the packages containing  the missing files and  append  them to
#  the 'missing_packages' parameter. Sometimes the  output of the  command (e.g.
#  'apt-file search <missing_file>') gives  several  packages. The program takes
#  the first one and check if  the  package is already  installed. If not, Tuxml
#  installs it. Else it installs the next one.
#  If tuxml reaches the end of the packages list without installing  any package
#  it means there is a problem with the missing file, so it returns an error.
#
#  @param   missing_files The  list  of  missing files whose  you  want  to find
#  associates packages
#  @param   missing_packages The list of missing packages you want to install
#
#  @returns -1 package not found
#  @returns  0 all dependencies were built
#
#  @warning Sometimes the  `apt-file search` command (or equivalent) gives several
#  packages. The program takes the first one and check if the package is already
#  installed. If not, tuxml installs it. Else it installs the next one until all
#  the package from the command above were installed.
def build_dependencies(missing_files, missing_packages):
    cmds = {
        "apt-get" : ["apt-file search {}", "dpkg-query -l | grep {}"],
        "pacman"  : ["pkgfile -d {}", "pacman -Fs {}"],
        "dnf"     : ["dnf whatprovides *{}", "rpm -qa | grep {}"],
        "yum"     : ["yum whatprovides *{}", "rpm -qa | grep {}"]
    }

    if tset.VERBOSE > 0 and len(missing_files) > 0:
        tcom.pprint(3, "This or those files are missing :")

    for mf in missing_files:
        if tset.VERBOSE > 0:
            print(" " * 4 + "- " + mf)

        if (tset.PKG_MANAGER is "pacman"):
            mf = mf.replace("/", " ")

        try:
            output = subprocess.check_output([cmds[tset.PKG_MANAGER][0].format(mf)], shell=True, universal_newlines=True)
            tdepLogger.log_candidates_packages(mf, output)
        except subprocess.CalledProcessError:
            tdepl.log_status(mf, False)
            tdepl.export_as_csv()
            tcom.pprint(1, "Unable to find the missing package")
            return -1

        # Sometimes the  output gives  several packages. The  program takes the
        # first one and check if the package is already installed. If not, tuxml
        # installs it. Else it installs the next one.
        lines = output.splitlines()
        i = 0
        status = 0
        while i < len(lines) and status == 0:
            package = lines[i].split(":")[0]
            # 0: package already installed
            # 1: package not installed
            status = subprocess.call([cmds[tset.PKG_MANAGER][1].format(package)], stdout=tset.OUTPUT, stderr=tset.OUTPUT, shell=True)
            if status == 1:
                tdepl.log_install(mf, package)
                missing_packages.append(package)
            i += 1

        # if tuxml reaches the end of the packages list without installing any package
        # it means that there is a problem with mf, so it returns an error
        if i > len(lines) and status == 0:
            tdepl.log_status(mf, False)
            tdepl.export_as_csv()
            tcom.pprint(1, "Unable to find the missing package")
            return -1
        else:
            tdepl.log_status(mf, True)

    tdepl.export_as_csv()
    tcom.pprint(0, "Dependencies built")
    return 0


## @author  LE FLEM Erwan
#  @author  MERZOUK Fahim
#
#  @brief   Check preinstalled package
#  @details Check which package are preinstalled among the list of given package,
#  useful to know which of the dependencies where already installed
#
#  @param dependencies list of packages
#
#  @returns list of already installed package amongt the list of given package
def get_installed_packages(dependencies):
    installed_packages = list()

    cmds = {
        "apt-get" : "dpkg -s  {}",
        "pacman"  : "pacman -Qs {} | grep \"/{} \"",
        "dnf"     : "rpm -qa | grep {}",
        "yum"     : [""]
        # "emerge": [],
        # "zypper": []
    }

    for dep in dependencies:
        try:
            status = subprocess.call([cmds[tset.PKG_MANAGER][0].format(dep,dep)], shell=True, universal_newlines=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            #status = subprocess.call([cmds.get("apt-get").format(dep, dep)], shell=True, universal_newlines=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            if (status == 0):
                installed_packages.append(dep)
        except subprocess.CalledProcessError:
            tcom.pprint(1, "Unable to build the list of installed packages.")
            return None
    return installed_packages


## @author LE FLEM Erwan
#  @author MERZOUK Fahim
#
#  @brief   Install minimal dependencies required to compile the kernel
#  @details Install the following packages :  gcc,  make, binutils,  util-linux,
#  e2fsprogs, bc. By "Minimal dependencies", we mean the dependencies that will
#  always be needed to compile the kernel, regardless of the config file.
#
#  @returns -1 Unable to install minimal dependencies
#  @returns  0 Minimal dependencies successfully installed
def install_minimal_dependencies():
    tcom.pprint(2, "Installing minimal dependencies")
    minimal_pkgs = ["gcc", "make", "binutils", "util-linux", "e2fsprogs", "bc"]

    if tcom.install_packages(minimal_pkgs) != 0:
        tcom.pprint(2, "Unable to install minimal dependencies.")
        return -1
    else:
        tcom.pprint(2, "Minimal dependencies successfully installed.")
        return 0


## @author LE FLEM Erwan
#  @author FAHIM Merzouk
#
#  @brief   Install default dependencies required to compile the kernel
#  @details Install the following packages : kmod, jfsutils, xfsprogs, btrfs-progs,
#  pcmciautils, ppp, grub, iptables, openssl, reiserfsprogs, squashfs-tools, quotatool,
#  nfs-kernel-server, procps, mcelog, libcrypto++6, apt-utils, gcc-6-plugin-dev,
#  libssl-dev.
#  Warning : names bases on debian packages, they may vary amongs distribution.
#
#  @returns -1 Unable to install some packages
#  @returns  0 Successfull installation
def install_default_dependencies():
    if (install_minimal_dependencies() != 0):
        return -1
    # Install packages common to all distro
    tcom.pprint(2, "Installing default dependencies")

    common_pkgs = ["kmod", "jfsutils", "xfsprogs", "btrfs-progs", "pcmciautils", "ppp", "grub","iptables","openssl"]

    # Now installation of packages with name that vary amongs distributions
    debian_specific = ["reiserfsprogs" , "squashfs-tools", "quotatool", "nfs-kernel-server", "procps", "mcelog", "libcrypto++6", "apt-utils", "gcc-6-plugin-dev", "libssl-dev"]
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
        tcom.pprint(2, "Unable to install default dependencies.")
        return -1
    else:
        tcom.pprint(2, "Default dependencies successfully installed.")
        return 0


# ============================================================================ #


if __name__ == '__main__':
    # cps = ["gcc", "make", "remake", "afur-makepkg", "xreader", "ppp", "grub","iptables","openssl", "bc"]
    # print(get_installed_packages(cps))
