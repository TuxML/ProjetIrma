#!/bin/python
import subprocess
import shutil

# authors : LE FLEM Erwan, MERZOUK Fahim
# Check if the given package manager is present on the system
# return true or false
def packageManagerIs(packageManagerName):
    return shutil.which(packageManagerName)

# authors : LE FLEM Erwan, MERZOUK Fahim
# get the package manager presents on the system
# return value :
#    as a String, the name of the first supported package manager, if any.
#    None if no supported packages manager has been found e.g apt-get.
def getPackageManager():
    pkg_managers = ["apt-get", "pacman", "dnf", "yum", "emerge", "zypper"]
    for manager in pkg_managers:
        if packageManagerIs(manager):
            return manager
    return None

# authors : LE FLEM Erwan, MERZOUK Fahim
# Install the list of given packages
# return 0 on sucess, -2 if no supported packages manager is found, and other code if the package managers failed installation.
def installPackages(listOfPackages,pkg_manager):
    managerToCmdInstall = {"apt-get": " -qq -y install ", "pacman": " -S --noconfirm ", "dnf": " -q install ", "yum": " -y install ", "emerge" : " --quiet-build=y -a ", "zypper":" --non-interactive install "}
    return subprocess.call([pkg_manager + managerToCmdInstall[pkg_manager] + " ".join(listOfPackages)], shell=True)

def update_system(pkg_manager):
    # TODO : check on https://wiki.archlinux.org/index.php/System_maintenance#Partial_upgrades_are_unsupported about potential issues using -Sy instead of -Syu before installing pkgs.
    managerToUpdate = {"apt-get": " update && apt-get upgrade", "pacman": " -Syu", "dnf": " update && dnf upgrade", "yum": " update", "emerge" : " --sync", "zypper":" refresh"}
    return subprocess.call([pkg_manager + managerToUpdate[pkg_manager]], shell=True)

    # if (code == 0):
    #     print("[+] Synchronized with package repository")
    # else:
    #     print("[-] Error while synchronizing with packages repository.")

#authors : LE FLEM Erwan, MERZOUK Fahim
#Install packages of required dependencies to compile the kernel
#return zero on sucess, - 2 if no packages manager is found on error, other values for installation error.
def installDependency():
    pkg_manager = getPackageManager();
    if (pkg_manager == None):
        print("[-] Unsupported package manager")
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
