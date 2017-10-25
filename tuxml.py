#!/usr/bin/python3

# compile, log analysis & dependencies imports
import os
import sys
import subprocess
import re
import shutil
import time
import sendDB


# === GLOBALS ===
PATH = ""
LOG_DIR = "/logs"
STD_LOG_FILE = LOG_DIR + "/std.logs"
ERR_LOG_FILE = LOG_DIR + "/err.logs"
DISTRO = ""
DEBUG = False
OUTPUT = sys.__stdout__
COUNTER = 0 # number of time the program had to recompile


# author : LEBRETON Mickael
#
# Get the package manager of the system
#
# return value :
#  -1 Distro not supported
#   0 Arch based distro
#   1 Debian based distro
#   2 RedHat based distro
def get_distro():
    package_managers = ["pacman", "apt-get", "dnf"]
    for pm in package_managers:
        try:
            distro = package_managers.index(shutil.which(pm).split("/")[3]) #/usr/bin/pacman --> pacman
        except Exception as err:
            distro = -1

        if 0 <= distro and distro < len(package_managers):
            return distro
    return -1


# author : LE FLEM Erwan, MERZOUK Fahim
#
# [check_dependencies description]
#
# return value :
#   0
#   1
def check_dependencies():
    print("[*] Checking dependencies")
    # TODO check_dependencies


# author : LEBRETON Mickael
#
# [install_missing_packages description]
#
## return value :
#   -1 distro not supported by TuxML
#    0 installation OK
def install_missing_packages(missing_files, missing_packages):
    # 0 Arch / 1 Debian / 2 RedHat
    if DISTRO > 2:
        print("[-] Distro not supported by TuxML")
        return -1

    if DEBUG:
        if DISTRO == 0:
            print("=== Arch based distro")
        elif DISTRO == 1:
            print("=== Debian based distro")
        elif DISTRO == 2:
            print("=== RedHat based distro")
        else:
            pass

    cmd_update = ["pacman -Sy", "apt-file update && apt-get update"]
    cmd_search = ["pkgfile -s {}", "apt-file search {}"]
    cmd_install = ["pacman --noconfirm -S ", "apt-get -y install "]

    if DEBUG:
        print("=== Those files are missing :")

    for mf in missing_files:
        # example : mf = "openssl/bio.h"
        if DEBUG:
            print("===" + mf)

        output = subprocess.check_output([cmd_search[DISTRO].format(mf)], shell=True)

        # some times the output gives several packages, the program takes the first one (== first line)
        line = output.decode("utf-8").splitlines()
        missing_packages.append(line[COUNTER].split(":")[0]) #debian and archway

    print("[*] Updating package database")
    subprocess.call([cmd_update[DISTRO]], stdout=OUTPUT, stderr=OUTPUT, shell=True)

    # BUG Des fois le gestionnaire de paquet ne trouve pas le paquet
    # Donc l'install des paquets plante mais la compile recommence
    # (compile à l'infini)
    # (cas de aicdb.h)
    print("[*] Installing missing packages : " + " ".join(missing_packages))
    subprocess.call([cmd_install[DISTRO] + " ".join(missing_packages)], stdout=OUTPUT, stderr=OUTPUT, shell=True)

    return 0


# author : LEBRETON Mickael
#
# [log_analysis description]
#
# return value :
#   -1 it wasn't able to find them
#    0 the program was able to find the missing package(s)
def log_analysis():
    global COUNTER

    print("[*] Analyzing error log file")

    missing_files = []
    missing_packages = []
    with open(PATH + ERR_LOG_FILE, "r") as err_logs:
        for line in err_logs:
            if re.search("fatal error", line):
                # case "file.c:48:19: fatal error: <file.h>: No such file or directory"
                missing_files.append(line.split(":")[4])
            elif re.search("Command not found", line):
                # case "make[4]: <command> : command not found"
                missing_packages.append(line.split(":")[1])
            elif re.search("not found", line):
                # case "/bin/sh: 1: <command>: not found"
                missing_files.append(line.split(":")[2])
            else:
                pass

    if len(missing_files) > 0 or len(missing_packages) > 0:
        status = install_missing_packages(missing_files, missing_packages)

        if status == 0:
            print("[+] Restarting compilation")
            COUNTER += 1
            return 0
        else:
            return -1
    else:
        print("[-] Unable to find the missing package(s)")
        return -1


# author : LEBRETON Mickael
#
# [compilation description]
#
# return value :
#   -1 compilation has failed but the program was able to find the missing package(s)
#   -2 compilation has failed and the program wasn't able to find the missing package(s)
#      (it means an unknow error)
#   >0 no error (time to compile in seconds)
def compile():
    print("[*] Compilation in progress");
    # barre de chargement [ ##########-------------------- ] 33%

    if not os.path.exists(PATH + LOG_DIR):
        os.makedirs(PATH + LOG_DIR)

    with open(PATH + STD_LOG_FILE, "w") as std_logs, open(PATH + ERR_LOG_FILE, "w") as err_logs:
        start_time = time.time()
        status = subprocess.call(["make", "-C", PATH, "-j", "6"], stdout=std_logs, stderr=err_logs)
        end_time = time.time()

    if status == 0:
        print("[+] Compilation done")
        return end_time - start_time
    else:
        print("[-] Compilation failed, exit status : {}".format(status))
        return log_analysis() - 1


# author : DUMANGET Dorian, MERZOUK Fahim
#
# [archi_is_64 description]
#
# return value :
#   True  Archi is 64 bits
#   False Archi is 32 bits
def archi_is_64():
    with open(PATH + "/.config") as config:
        for line in config:
            if re.search("CONFIG_OUTPUT_FORMAT", line):
                return not re.search("elf32-i386", line)


# === MAIN FUNCTION ===
if len(sys.argv) < 2 or os.getuid() != 0:
    print("[*] USE : ./tuxml.py <path/to/the/linux/sources/directory> [option1 option2 ...]")
    print("[*] Please run TuxML as root")
    print("[*] Available options :")
    print("\t--debug\t\tTuxML is more verbose and do not generate a new config file")
    print("\t--version\tDisplay the version of TuxML")
    sys.exit(-1)

PATH = sys.argv[1]
DISTRO = get_distro()

# import command/command line ??? ==> plus propre (parsing arguments)
if "--version" in sys.argv:
    print("TuxML v0.1")
    sys.exit(0)

if "--debug" in sys.argv:
    DEBUG = True
    OUTPUT = sys.__stdout__
    print("=== Debug mode enabled")
    print("[*] Cleaning previous compilation")
    subprocess.call(["make", "-C", PATH, "clean"], stdout=OUTPUT, stderr=OUTPUT)
else:
    DEBUG = False
    OUTPUT = subprocess.DEVNULL

    print("[*] Cleaning previous compilation")
    subprocess.call(["make", "-C", PATH, "mrproper"], stdout=OUTPUT, stderr=OUTPUT)

    amd64 = False
    print("[*] Generating random config")
    while not amd64:
        subprocess.call(["make", "-C", PATH, "randconfig"], stdout=OUTPUT, stderr=OUTPUT)
        amd64 = archi_is_64()


check_dependencies()

status = -1
while (status == -1):
    if DEBUG:
        print("=== Counter : {}".format(COUNTER))
    status = compile()

if status >= 0:
    print("[+] Testing the kernel config")
    print("[+] Successfully compiled in " + time.strftime("%H:%M:%S", time.gmtime(status)) + ", sending data")
else:
    # status == -2
    print("[-] Unable to compile using this config or another error happened, sending data anyway")

sendDB.send_data(PATH, ERR_LOG_FILE, status)
