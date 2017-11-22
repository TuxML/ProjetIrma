#!/usr/bin/python3

import os
import sys
import subprocess
import re
import shutil
import time
import tuxml_sendDB as tsen
import tuxml_common as tcom
import tuxml_settings as tset
import tuxml_depman as tdep

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
# TODO fusionner get_distro et tcom.get_package_manager (common)
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
#   -3 distro or package manager not supported by TuxML
#   -2 sys update failed
#   -1 package(s) not found
#    0 installation OK
def install_missing_packages(missing_files, missing_packages):
    distro = get_distro()

    if distro > 2:
        tcom.pprint(1, "Distro not supported by TuxML")
        return -3

    if distro == 0:
        pkgs = tdep.build_dependencies_arch(missing_files, missing_packages);
    elif distro == 1:
        pkgs = tdep.build_dependencies_debian(missing_files, missing_packages);
    elif distro == 2:
        pkgs = tdep.build_dependencies_redhat(missing_files, missing_packages);
    else:
        pass

    pkg_manager = tcom.get_package_manager()
    if pkg_manager == None:
        return -3

    if tcom.update_system(pkg_manager) != 0:
        return -2

    if tcom.install_packages(pkg_manager, pkgs) != 0:
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
    tcom.pprint(2, "Analyzing error log file")

    missing_packages = []
    missing_files    = []
    with open(tset.PATH + tset.ERR_LOG_FILE, "r") as err_logs:
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
            tcom.pprint(0, "Restarting compilation")
            return 0
        else:
            return -1
    else:
        tcom.pprint(1, "Unable to find the missing package(s)")
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
    tcom.pprint(2, "Compilation in progress")

    # TODO barre de chargement [ ##########-------------------- ] 33%

    if not os.path.exists(tset.PATH + tset.LOG_DIR):
        os.makedirs(tset.PATH + tset.LOG_DIR)

    with open(tset.PATH + tset.STD_LOG_FILE, "w") as std_logs, open(tset.PATH + tset.ERR_LOG_FILE, "w") as err_logs:
        status = subprocess.call(["make", "-C", tset.PATH, "-j", "6"], stdout=std_logs, stderr=err_logs)

    if status == 0:
        tcom.pprint(0, "Compilation done")
        return 0
    else:
        tcom.pprint(2, "Compilation failed, exit status : {}".format(status))
        return log_analysis() - 1


# === MAIN FUNCTION ===
# TODO import command/command line ??? ==> plus propre (parsing arguments)
if "-h" in sys.argv or "--help" in sys.argv:
    print("[*] USE : sudo ./tcom.py </path/to/sources/directory> [option1 option2 ...]")
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
    tcom.pprint(1, "Bad parameters, use --help to print help")
    sys.exit(-1)

if os.getuid() != 0:
    tcom.pprint(1, "Please run TuxML as root, use --help to print help")
    sys.exit(-1)

if "-d" in sys.argv or "--debug" in sys.argv:
    tset.DEBUG  = True
    tset.OUTPUT = sys.__stdout__
    date = time.strftime("%H:%M:%S", time.gmtime(time.time()))
    tcom.pprint(3, "Debug mode ON")
else:
    tset.DEBUG  = False
    tset.OUTPUT = subprocess.DEVNULL

tcom.pprint(2, "Cleaning previous compilation")

tset.PATH = sys.argv[1]
if "--no-randconfig" in sys.argv:
    subprocess.call(["make", "-C", tset.PATH, "clean"], stdout=tset.OUTPUT, stderr=tset.OUTPUT)
else:
    subprocess.call(["make", "-C", tset.PATH, "mrproper"], stdout=tset.OUTPUT, stderr=tset.OUTPUT)
    tcom.pprint(2, "Generating new config file")
    output = subprocess.call(["KCONFIG_ALLCONFIG=" + os.path.dirname(os.path.abspath(__file__)) + "/tuxml.config make -C " + tset.PATH + " randconfig"], stdout=tset.OUTPUT, stderr=tset.OUTPUT, shell=True)

tcom.pprint(0, "Checking dependencies")

start_time = time.time()
status = -1
while status == -1:
    status = compile()
end_time = time.time()

if status == 0:
    tcom.pprint(0, "Testing the kernel config")
    status = end_time - start_time
    compile_time = time.strftime("%H:%M:%S", time.gmtime(status))
    tcom.pprint(0, "Successfully compiled in {}, sending data".format(compile_time))
else:
    # status == -2
    tcom.pprint(1, "Unable to compile using this config or another error happened, sending data anyway")

# tsen.send_data(tset.PATH, tset.ERR_LOG_FILE, status)
