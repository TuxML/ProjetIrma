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

import subprocess
import shutil
import time
import sys
import tuxml_settings as tset


# author : LEBRETON Mickael
#
# Pretty Printer which allow us to print the date in VERBOSE mod
def pprint(s, message):
    code = [
        tset.LIGHT_GREEN,     # success
        tset.LIGHT_RED,       # error
        tset.WHITE,           # default
        tset.GRAY,            # debug
        tset.LIGHT_ORANGE     # warning
    ]

    NC = tset.WHITE

    date    = tset.LIGHT_BLUE_1 + time.strftime("[%Y-%m-%d %H:%M:%S GMT] ", time.localtime(time.time()))
    func    = tset.GRAY + "[" + sys._getframe(1).f_code.co_name + "] "
    msg     = code[s] + message + NC

    # TODO rediriger vers la sortie standard et la sortie d'erreur
    if tset.VERBOSE == 1:
        print(msg)
    elif tset.VERBOSE == 2:
        print(date + msg)
    else:
        print(date + func + msg)


# authors : LE FLEM Erwan, MERZOUK Fahim
#
# Get the package manager presents on the system
#
# return value :
#    String The name of the first supported package manager
#    None   If no supported packages manager has been found
def get_package_manager():
    pprint(2, "Finding package manager")

    pkg_managers = ["apt-get", "pacman", "dnf", "yum", "emerge", "zypper"]
    for manager in pkg_managers:
        if shutil.which(manager): # remplacer par shutil.which(manager) ???
            pprint(0, "Package manager is " + manager)
            return manager

    pprint(1, "Unsupported package manager")
    return None


# authors : LE FLEM Erwan, MERZOUK Fahim, LEBRETON Mickaël
#
# Install the list of given packages
#
# return value :
#   -2 Package manager not supported
#   -1 Unable to install the packages
#    0 Successfull install
def install_packages(missing_packages):
    pprint(2, "Installing packages : " + " ".join(missing_packages))

    manager_to_cmd = {
        "apt-get": " -y install ",
        "pacman": " -S --noconfirm ",
        "dnf": " -q install ",
        "yum": " -y install ",
        "emerge" : " --quiet-build=y -a ",
        "zypper": " --non-interactive install "
    }

    status = subprocess.call([tset.PKG_MANAGER + manager_to_cmd[tset.PKG_MANAGER] + " ".join(missing_packages)], stdout=tset.OUTPUT, stderr=tset.OUTPUT, shell=True)

    if status != 0:
        pprint(1, "Some packages were not found, installation stoped")
        return -1
    else:
        pprint(0, "All the packages were found and installed")
        return 0


# authors : LE FLEM Erwan, MERZOUK Fahim, LEBRETON Mickaël
#
# Update the package database
#
# return value :
#   -1 Unable to update the package databate
#    0 Successfull update
def update_system():
    # TODO : check on
    # https://wiki.archlinux.org/index.php/System_maintenance#Partial_upgrades_are_unsupported
    # about potential issues using -Sy instead of -Syu before installing pkgs.

    pprint(2, "Updating packages repositories")

    manager_to_cmd = {
        "apt-get": " update && apt-file update",
        "pacman": " -Sy",
        "dnf": " -y update",
        "yum": " -y update",
        "emerge" : " --sync",
        "zypper": " refresh"
    }

    print(tset.GRAY, end='')
    status = subprocess.call([tset.PKG_MANAGER + manager_to_cmd[tset.PKG_MANAGER]], stdout=tset.OUTPUT, stderr=tset.OUTPUT, shell=True)

    if status != 0:
        pprint(1, "Error while updating packages repositories")
        return -1
    else:
        pprint(0, "Packages repositories updated")
        return 0
