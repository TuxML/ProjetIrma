#!/bin/python
import subprocess
import shutil

# author : LE FLEM Erwan, MERZOUK Fahim
# Check if the given package manager is present on the system
# return true or false
def packageManagerIs(packageManagerName):
    return shutil.which(packageManagerName)

# author : LE FLEM Erwan, MERZOUK Fahim
# get the package manager present on the system
# return value :
#    as a String, the name of the first supported package manager, if any.
#    None if no supported packages manager has been found e.g pacman.
def getPackageManager():
    pkg_managers = ["apt-get", "pacman", "dnf", "yum", "emerge", "zypper"]
    for manager in pkg_managers:
        if packageManagerIs(manager):
            return manager
    return None

# author : LE FLEM Erwan, MERZOUK Fahim
# Install the list of given packages
# return 0 on sucess, -2 if no supported packages manager is found, and other code for other error.
def installPackages(listOfPackages):
    managerToCmdInstall = {"apt-get": " -qq -y install ", "pacman": " -S --noconfirm ", "dnf": " -q install ", "yum": " -y install ", "emerge" : " --quiet-build=y -a ", "zypper":" --non-interactive install "}
    pkg_manager = getPackageManager();
    if(pkg_manager != None):
        completedProcess = subprocess.run([pkg_manager + managerToCmdInstall[pkg_manager] + " ".join(listOfPackages)], shell=True)
        return completedProcess.returncode
    else:
        print("[-] Unsupported package manager")
        return -2

# author : LE FLEM Erwan, MERZOUK Fahim
# Install packages of required dependencies to compile the kernel
#return zero on sucess, =/= on error.
def installDependency():
    pkg_manager = getPackageManager();

    if (pkg_manager == None):
        print("[-] Unsupported package manager")
        return -2
    # TODO : check on https://wiki.archlinux.org/index.php/System_maintenance#Partial_upgrades_are_unsupported about issues using -Sy instead of -Syu before installing pkgs.
    managerToUpdate = {"apt-get": " update", "pacman": " -Sy", "dnf": " update", "yum": " update", "emerge" : " --sync", "zypper":" refresh"}
    completedProcess = subprocess.run([pkg_manager + managerToUpdate[pkg_manager]], shell=True)
    if (completedProcess.returncode == 0):
        print("[+] Synchronized with package repository")
    else:
        print("[-] Error while synchronizing with packages repository.")

    common_pkg = ["gcc", "make", "binutils", "util-linux", "kmod", "e2fsprogs", "jfsutils", "xfsprogs", "btrfs-progs", "pcmciautils", "ppp", "grub","iptables","openssl", "bc"]
    print("[*] Installation...")
    returnCode = installPackages(common_pkg)
    # Now packages with non common name.
    debian_specific = ["reiserfsprogs", "squashfs","quotatool", "nfs-kernel-server","procps", "mcelog", "libcrypto++6"]

    arch_specific = ["reiserfsprogs", "squashfs-tools","quota-tools", "isdn4k-utils", "nfs-utils", "procps-ng", "oprofile"]

    redHat_specific =  ["reiserfs-utils", "squashfs-tools", "quotatool","isdn4k-utils", "nfs-utils", "procps-ng", "oprofile", "mcelog"]

    gentoo_specific =  ["reiserfsprogs", "squashfs-tools", "quotatool", "nfs-utils", "procps", "mcelog", "oprofile"]

    suse_specific =  ["reiserfs", "quota", "nfs-client", "procps"]

    packageSpecific = {"apt-get" : debian_specific, "pacman" : arch_specific, "dnf":redHat_specific, "yum":redHat_specific, "emerge":gentoo_specific, "zypper":suse_specific}
    installPackages(packageSpecific[pkg_manager])

installDependency()
