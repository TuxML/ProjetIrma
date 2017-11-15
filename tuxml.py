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
            distro = package_managers.index(shutil.which(pm).split("/")[3])
        except Exception as err:
            distro = -1

        if 0 <= distro and distro < len(package_managers):
            return distro
    return -1


# author : LEBRETON Mickael
#
# [install_missing_packages description]
#
# return value :
#   -2 package not found
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

    cmd_update  = ["pacman -Sy", "apt-file update && apt-get update"]
    cmd_check   = ["/", "dpkg-query -l | grep {}"]
    cmd_search  = ["pkgfile -s {}", "apt-file search {}"] #pkgfile -s openssl/bio.h ne marche pas
    cmd_install = ["pacman --noconfirm -S ", "apt-get -y install "]

    if DEBUG:
        print("=== Those files are missing :")

    for mf in missing_files:
        if DEBUG:
            print("===" + mf)

        output = subprocess.check_output([cmd_search[DISTRO].format(mf)], shell=True)

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
            status = subprocess.call([cmd_check[DISTRO].format(package)], stdout=OUTPUT, stderr=OUTPUT, shell=True)
            print("=== {} not installed".format(package))
            if status == 1:
                missing_packages.append(package)
            i += 1

    print("[*] Updating package database")
    subprocess.call([cmd_update[DISTRO]], stdout=OUTPUT, stderr=OUTPUT, shell=True)

    print("[*] Installing missing packages : " + " ".join(missing_packages))
    status = subprocess.call([cmd_install[DISTRO] + " ".join(missing_packages)], stdout=OUTPUT, stderr=OUTPUT, shell=True)

    if status != 0:
        print("[-] Some packages were not found, installation stoped")
        return -2

    print("[+] All the missing packages were found and installed")
    return 0


# author : LEBRETON Mickael
#
# [log_analysis description]
#
# return value :
#   -1 it wasn't able to find them
#    0 the program was able to find the missing package(s)
def log_analysis():
    print("[*] Analyzing error log file")

    missing_packages = []
    missing_files    = []
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
            return 0
        else:
            return -1
    else:
        print("[-] Unable to find the missing package(s)")
        return -1


# author : LEBRETON Mickael
#
# [compile description]
#
# return value :
#   -1 compilation has failed but the program was able to find the missing package(s)
#   -2 compilation has failed and the program wasn't able to find the missing package(s)
#      (it means an unknow error)
#    0 no error (time to compile in seconds)
def compile():
    print("[*] Compilation in progress");

    # TODO barre de chargement [ ##########-------------------- ] 33%

    if not os.path.exists(PATH + LOG_DIR):
        os.makedirs(PATH + LOG_DIR)

    with open(PATH + STD_LOG_FILE, "w") as std_logs, open(PATH + ERR_LOG_FILE, "w") as err_logs:
        status = subprocess.call(["make", "-C", PATH, "-j", "6"], stdout=std_logs, stderr=err_logs)

    if status == 0:
        print("[+] Compilation done")
        return 0
    else:
        print("[-] Compilation failed, exit status : {}".format(status))
        return log_analysis() - 1


# === MAIN FUNCTION ===
# TODO import command/command line ??? ==> plus propre (parsing arguments)
if "-h" in sys.argv or "--help" in sys.argv:
    print("[*] USE : sudo ./tuxml.py </path/to/sources/directory> [option1 option2 ...]")
    print("[*] Available options :")
    print("\t-d  --debug\t\tTuxML is more verbose")
    print("\t-h  --help\t\tPrint this")
    print("\t    --no-randconfig\tDo not generate a new config file")
    print("\t-v  --version\t\tDisplay the version of TuxML")
    sys.exit(0)

if "-v" in sys.argv or "--version" in sys.argv:
    print("TuxML v0.1")
    sys.exit(0)

if os.getuid() != 0:
    print("[-] Please run TuxML as root, use --help to print help")
    sys.exit(-1)

if len(sys.argv) < 2:
    print("[-] Bad parameters, use --help to print help")
    sys.exit(-1)

PATH = sys.argv[1]
DISTRO = get_distro()

if "-d" in sys.argv or "--debug" in sys.argv:
    DEBUG  = True
    OUTPUT = sys.__stdout__
    print("=== Debug mode enabled at {}".format(time.strftime("%H:%M:%S", time.gmtime(time.time()))))
else:
    DEBUG  = False
    OUTPUT = subprocess.DEVNULL

print("[*] Cleaning previous compilation")

if "--no-randconfig" in sys.argv:
    subprocess.call(["make", "-C", PATH, "clean"], stdout=OUTPUT, stderr=OUTPUT)
else:
    subprocess.call(["make", "-C", PATH, "mrproper"], stdout=OUTPUT, stderr=OUTPUT)
    print("[*] Generating new config file")
    output = subprocess.call(["KCONFIG_ALLCONFIG=" + os.getcwd() + "/tuxml.config make -C " + PATH + " randconfig"], stdout=OUTPUT, stderr=OUTPUT, shell=True)

print("[+] Checking dependencies -- TODO")

start_time = time.time()
status = -1
while status == -1:
    status = compile()
end_time = time.time()

if status == 0:
    print("[+] Testing the kernel config -- TODO")
    status = end_time - start_time
    print("[+] Successfully compiled in " + time.strftime("%H:%M:%S", time.gmtime(status)) + ", sending data")
else:
    # status == -2
    print("[-] Unable to compile using this config or another error happened, sending data anyway")

sendDB.send_data(PATH, ERR_LOG_FILE, status)
