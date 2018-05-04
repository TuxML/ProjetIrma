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

## @file tuxml_common.py
#  @author LE FLEM Erwan
#  @author LEBRETON Mickaël
#  @author MERZOUK Fahim
#  @copyright Apache License 2.0
#  @brief This file contains all the functions used in all tuxml_* scripts
#  @copyright Apache License, Version 2.0

import subprocess
import shutil
import time
import sys
import tuxml_settings as tset


## @author  LEBRETON Mickaël
#
#  @brief   Usefull to print a message with the date, color code etc easily
#
#  @param   s       The status of the message (0 : success, 1 : error, 2 : default, 4 : debug, 5 : warning)
#  @param   message The message you want to print
#
#  @todo redirect messages to stdout and stderr if needed
def pprint(s, message):
    if s < 0 or s > 4:
        s = 2

    code = [
        tset.COLORS["light_green"],  # success
        tset.COLORS["light_red"],    # error
        tset.COLORS["white"],        # default
        tset.COLORS["gray"],         # debug
        tset.COLORS["light_orange"]  # warning
    ]

    NC = tset.COLORS["white"]

    date    = tset.COLORS["light_blue_1"] + time.strftime("[%Y-%m-%d %H:%M:%S %Z] ", time.localtime(time.time()))
    func    = tset.COLORS["gray"] + "[" + sys._getframe(1).f_code.co_name + "] "
    msg     = code[s] + message + NC

    if tset.VERBOSE == 1:
        print(msg)
    elif tset.VERBOSE == 2:
        print(date + msg)
    else:
        print(date + func + msg)


## @author  LE FLEM Erwan
#  @author  MERZOUK Fahim
#
#  @brief   Get the package manager presents on the system
#  @details The currently well suported packages manager are apt-get, pacman and dnf.
#
#  @returns String The name of the first supported package manager
#  @returns None   If no supported packages manager has been found
def get_package_manager():
    pprint(2, "Finding package manager")

    pkg_managers = ["apt-get", "pacman", "dnf", "yum", "emerge", "zypper"]
    for manager in pkg_managers:
        if shutil.which(manager): # remplacer par shutil.which(manager) ???
            pprint(0, "Package manager is " + manager)
            return manager

    pprint(1, "Unsupported package manager")
    return None


## @author  LE FLEM Erwan
#  @author  LEBRETON Mickaël
#  @author  MERZOUK Fahim
#
#  @brief   Install the list of given packages
#
#  @param   packages The list of missing packages you want to install
#
#  @returns -1 Unable to install the packages
#  @returns  0 Successfull installation
def install_packages(packages):
    pprint(2, "Installing packages : " + " ".join(packages))

    manager_to_cmd = {
        "apt-get": " -y install ",
        "pacman": " -S --noconfirm ",
        "dnf": " -q install ",
        "yum": " -y install ",
        "emerge" : " --quiet-build=y -a ",
        "zypper": " --non-interactive install "
    }

    status = subprocess.call([tset.PKG_MANAGER + manager_to_cmd[tset.PKG_MANAGER] + " ".join(packages)], stdout=tset.OUTPUT, stderr=tset.OUTPUT, shell=True)

    if status != 0:
        pprint(1, "Some packages were not found, installation stoped")
        return -1
    else:
        pprint(0, "All the packages were found and installed")
        return 0


## @author  LE FLEM Erwan
#  @author  LEBRETON Mickaël
#  @author  MERZOUK Fahim
#
#  @brief   Update the package database
#
#  @returns -1 Unable to update the package databate
#  @returns  0 Successfull update
#
#  @todo check on https://wiki.archlinux.org/index.php/System_maintenance#Partial_upgrades_are_unsupported
#  about potential issues using -Sy instead of -Syu before installing pkgs.
def update_system():
    pprint(2, "Updating packages repositories")

    manager_to_cmd = {
        "apt-get": " update && apt-file update",
        "pacman": " -Sy",
        "dnf": " -y update",
        "yum": " -y update",
        "emerge" : " --sync",
        "zypper": " refresh"
    }

    status = subprocess.call([tset.PKG_MANAGER + manager_to_cmd[tset.PKG_MANAGER]], stdout=tset.OUTPUT, stderr=tset.OUTPUT, shell=True)

    if status != 0:
        pprint(1, "Error while updating packages repositories")
        return -1
    else:
        pprint(0, "Packages repositories updated")
        return 0
