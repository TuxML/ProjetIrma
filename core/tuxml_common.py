import subprocess
import shutil
import time
import tuxml_settings as tset


# author : LEBRETON Mickael
#
# Pretty Printer which allow us to print the date in VERBOSE mod
def pprint(s, message):
    # success, error, message, debug, warning
    status = ["[+]", "[-]", "[*]", "[#]", "[!]"]

    date = time.strftime("%Y-%m-%d %H:%M:%S | ", time.gmtime(time.time()))

    if tset.VERBOSE:
        print(status[s] + " " + date + message)
    else:
        print(status[s] + " " + message)


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
    # TODO : check on https://wiki.archlinux.org/index.php/System_maintenance#Partial_upgrades_are_unsupported about potential issues using -Sy instead of -Syu before installing pkgs.

    pprint(2, "Updating packages repositories")

    manager_to_cmd = {
        "apt-get": " update && apt-file update",
        "pacman": " -Sy",
        "dnf": " update",
        "yum": " update",
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
