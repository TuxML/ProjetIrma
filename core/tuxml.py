#!/usr/bin/python3

import os
import sys
import subprocess
import re
import shutil
import time
import tuxml_sendDB
import tuxml_common
import tuxml_settings


# author : LEBRETON Mickael
#
# Get the package manager of the system
#
# return value :
#  -1 Distro not supported
#   0 Arch based distro
#   1 Debian based distro
#   2 RedHat based distro
#
# TODO fusionner get_distro et tuxml_common.get_package_manager (common)
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


# author : LE FLEM Erwan
#
# [build_dependencies_arch description]
#
# return value :
#   -1 package not found
#    0 installation OK
def build_dependencies_arch(missing_files, missing_packages):
    if tuxml_settings.DEBUG:
        tuxml_common.pprint(3, "Arch based distro")

    cmd_check   = ""
    cmd_search  = "pkgfile -s {}" #pkgfile -s openssl/bio.h ne marche pas

    return 0


# author : LEBRETON Mickael
#
# [build_dependencies_debian description]
#
# return value :
#   -1 package not found
#    0 installation OK
def build_dependencies_debian(missing_files, missing_packages):
    if tuxml_settings.DEBUG:
        tuxml_common.pprint(3, "Debian based distro")

    cmd_search  = "apt-file search {}" # cherche dans quel paquet est le fichier
    cmd_check   = "dpkg-query -l | grep {}" # vérifie si le paquet est présent sur le système

    if tuxml_settings.DEBUG and len(missing_files) > 0:
        tuxml_common.pprint(3, "Those files are missing :")

    for mf in missing_files:
        if tuxml_settings.DEBUG:
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
            status = subprocess.call([cmd_check.format(package)], stdout=tuxml_settings.OUTPUT, stderr=tuxml_settings.OUTPUT, shell=True)
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
    if tuxml_settings.DEBUG:
        tuxml_common.pprint(3, "RedHat based distro")

    return 0


# author : LEBRETON Mickael
#
# [install_missing_packages description]
#
# return value :
#   -3 distro or package manager not supported by TuxML
#   -2 sys update failed
#   -1 package(s) not found
#    0 installation OK
def install_missing_packages(missing_files, missing_packages):
    distro = get_distro()

    if distro > 2:
        tuxml_common.pprint(1, "Distro not supported by TuxML")
        return -3

    if distro == 0:
        pkgs = build_dependencies_arch(missing_files, missing_packages);
    elif distro == 1:
        pkgs = build_dependencies_debian(missing_files, missing_packages);
    elif distro == 2:
        pkgs = build_dependencies_redhat(missing_files, missing_packages);
    else:
        pass

    pkg_manager = tuxml_common.get_package_manager()
    if pkg_manager == None:
        return -3

    if tuxml_common.update_system(pkg_manager) != 0:
        return -2

    if tuxml_common.install_packages(pkg_manager, pkgs) != 0:
        return -1

    return 0


# author : LEBRETON Mickael
#
# [log_analysis description]
#
# return value :
#   -1 it wasn't able to find them
#    0 the program was able to find the missing package(s)
def log_analysis():
    tuxml_common.pprint(2, "Analyzing error log file")

    missing_packages = []
    missing_files    = []
    with open(tuxml_settings.PATH + tuxml_settings.ERR_LOG_FILE, "r") as err_logs:
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
            tuxml_common.pprint(0, "Restarting compilation")
            return 0
        else:
            return -1
    else:
        tuxml_common.pprint(1, "Unable to find the missing package(s)")
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
    tuxml_common.pprint(2, "Compilation in progress")

    # TODO barre de chargement [ ##########-------------------- ] 33%

    if not os.path.exists(tuxml_settings.PATH + tuxml_settings.LOG_DIR):
        os.makedirs(tuxml_settings.PATH + tuxml_settings.LOG_DIR)

    with open(tuxml_settings.PATH + tuxml_settings.STD_LOG_FILE, "w") as std_logs, open(tuxml_settings.PATH + tuxml_settings.ERR_LOG_FILE, "w") as err_logs:
        status = subprocess.call(["make", "-C", tuxml_settings.PATH, "-j", "6"], stdout=std_logs, stderr=err_logs)

    if status == 0:
        tuxml_common.pprint(0, "Compilation done")
        return 0
    else:
        tuxml_common.pprint(2, "Compilation failed, exit status : {}".format(status))
        return log_analysis() - 1


# === MAIN FUNCTION ===
# TODO import command/command line ??? ==> plus propre (parsing arguments)
if "-h" in sys.argv or "--help" in sys.argv:
    print("[*] USE : sudo ./tuxml_common.py </path/to/sources/directory> [option1 option2 ...]")
    print("[*] Available options :")
    print("\t-d  --debug\t\tTuxML is more verbose")
    print("\t-h  --help\t\tPrint this")
    print("\t    --no-randconfig\tDo not generate a new config file")
    print("\t-v  --version\t\tDisplay the version of TuxML")
    sys.exit(0)

if "-v" in sys.argv or "--version" in sys.argv:
    print("TuxML v0.2")
    sys.exit(0)

if len(sys.argv) < 2:
    tuxml_common.pprint(1, "Bad parameters, use --help to print help")
    sys.exit(-1)

if os.getuid() != 0:
    tuxml_common.pprint(1, "Please run TuxML as root, use --help to print help")
    sys.exit(-1)

if "-d" in sys.argv or "--debug" in sys.argv:
    tuxml_settings.DEBUG  = True
    tuxml_settings.OUTPUT = sys.__stdout__
    date = time.strftime("%H:%M:%S", time.gmtime(time.time()))
    tuxml_common.pprint(3, "Debug mode ON")
else:
    tuxml_settings.DEBUG  = False
    tuxml_settings.OUTPUT = subprocess.DEVNULL

tuxml_common.pprint(2, "Cleaning previous compilation")

tuxml_settings.PATH = sys.argv[1]
if "--no-randconfig" in sys.argv:
    subprocess.call(["make", "-C", tuxml_settings.PATH, "clean"], stdout=tuxml_settings.OUTPUT, stderr=tuxml_settings.OUTPUT)
else:
    subprocess.call(["make", "-C", tuxml_settings.PATH, "mrproper"], stdout=tuxml_settings.OUTPUT, stderr=tuxml_settings.OUTPUT)
    tuxml_common.pprint(2, "Generating new config file")
    print(os.getcwd())
    output = subprocess.call(["KCONFIG_ALLCONFIG=" + os.getcwd() + "/tuxml.config make -C " + tuxml_settings.PATH + " randconfig"], stdout=tuxml_settings.OUTPUT, stderr=tuxml_settings.OUTPUT, shell=True)

tuxml_common.pprint(0, "Checking dependencies")

start_time = time.time()
status = -1
while status == -1:
    status = compile()
end_time = time.time()

if status == 0:
    tuxml_common.pprint(0, "Testing the kernel config")
    status = end_time - start_time
    compile_time = time.strftime("%H:%M:%S", time.gmtime(status))
    tuxml_common.pprint(0, "Successfully compiled in {}, sending data".format(compile_time))
else:
    # status == -2
    tuxml_common.pprint(1, "Unable to compile using this config or another error happened, sending data anyway")

# tuxml_sendDB.send_data(tuxml_settings.PATH, tuxml_settings.ERR_LOG_FILE, status)
