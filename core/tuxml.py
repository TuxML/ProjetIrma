#!/usr/bin/python3

import os
import sys
import subprocess
import re
import shutil
import time
import curses
import tuxml_sendDB as tsen
import tuxml_common as tcom
import tuxml_settings as tset
import tuxml_depman as tdep
import tuxml_environment as tenv
import tuxml_bootCheck as tbch
import tuxml_argshandler as targs


# author : LEBRETON Mickael
#
# This function installs the missing packages
#
# return value :
#   -1 package(s) not found
#    0 installation OK
def install_missing_packages(missing_files, missing_packages):
    if tdep.build_dependencies(missing_files, missing_packages) != 0:
        return -1

    if tcom.install_packages(missing_packages) != 0:
        return -1

    return 0


# author : LEBRETON Mickael
#
# This function analyzes the error log file and try to find the missing packages
# and the missings files
#
# return value :
#   -1 the program wasn't able to find the missing package(s)
#    0 the program was able to find the missing package(s)
def log_analysis(missing_files, missing_packages):
    tcom.pprint(2, "Analyzing error log file")

    with open(tset.PATH + tset.ERR_LOG_FILE, "r") as err_logs:
        for line in err_logs:
            if re.search("fatal error", line):
                # case "file.c:48:19: fatal error: <file.h>: No such file or directory"
                missing_files.append(line.split(":")[4])
            elif re.search("Command not found", line):
                # case "make[4]: <command> : command not found"
                missing_packages.append(line.split(":")[1])
            elif re.search("not found", line):
                if len(line.split(":")) == 4:
                    # case "/bin/sh: 1: <command>: not found"
                    missing_files.append(line.split(":")[2])
                else:
                    # ./scripts/gcc-plugin.sh: 11: ./scripts/gcc-plugin.sh: <package>: not found
                    missing_packages.append(line.split(":")[3])
            else:
                pass

    if len(missing_files) > 0 or len(missing_packages) > 0:
        tcom.pprint(0, "Missing file(s)/package(s) found")
        return 0
    else:
        tcom.pprint(1, "Unable to find the missing package(s)")
        return -1


# author : LEBRETON Mickael
#
# This  function  starts the  compilation and redirects  the  logs to  the files
# std.logs and err.logs
#
# return value :
#   -1 compilation has failed
#    0 no error (time to compile in seconds)
def compilation():
    tcom.pprint(2, "Compilation in progress")

    # TODO barre de chargement [ ##########-------------------- ] 33%

    if not os.path.exists(tset.PATH + tset.LOG_DIR):
        os.makedirs(tset.PATH + tset.LOG_DIR)

    with open(tset.PATH + tset.STD_LOG_FILE, "w") as std_logs, open(tset.PATH + tset.ERR_LOG_FILE, "w") as err_logs:
        status = subprocess.call(["make", "-C", tset.PATH, "-j" + str(tset.NB_CORES)], stdout=std_logs, stderr=err_logs)

    if status == 0:
        tcom.pprint(0, "Compilation done")
        return 0
    else:
        tcom.pprint(2, "Compilation failed, exit status : {}".format(status))
        return -1


def init_launcher():
    # get environment details
    tset.TUXML_ENV = tenv.get_environment_details()

    # get the package manager
    tset.PKG_MANAGER = tcom.get_package_manager()
    if tset.PKG_MANAGER == None:
        return -1

    # updating package database
    if tcom.update_system() != 0:
        return -2

    # install default packages
    if tdep.install_default_dependencies() != 0:
        return -3

    return 0


# author : LEBRETON Mickael
#
# [description]
#
# return value :
#   -1 Unable to generate KCONFIG
#    0 no error
def gen_config(Kconfig=None):
    if Kconfig:
        try:
            # debug config with given KCONFIG_SEED
            int(Kconfig, 16)
            tcom.pprint(2, "Generating config file with KCONFIG_SEED=" + Kconfig)
            status = subprocess.call(["KCONFIG_SEED=" + Kconfig + " make -C " + tset.PATH + " randconfig"], stdout=tset.OUTPUT, stderr=tset.OUTPUT, shell=True)
        except ValueError:
            # debug config with given KCONFIG_FILE
            if os.path.exists(Kconfig):
                tcom.pprint(2, "Using KCONFIG_FILE " + Kconfig)
                shutil.copyfile(Kconfig, tset.PATH + "/.config") # TODO maybe a better way ?
                return 0
            else:
                tcom.pprint(1, "KCONFIG_FILE doesn't exist")
                return -1
    else:
        # generating new KConfig file
        tcom.pprint(2, "Randomising new KCONFIG_FILE")
        status = subprocess.call(["KCONFIG_ALLCONFIG=" + os.path.dirname(os.path.abspath(__file__)) + "/tuxml.config make -C " + tset.PATH + " randconfig"], stdout=tset.OUTPUT, stderr=tset.OUTPUT, shell=True)

    # testing status after subprocess call to make randconfig
    if status != 0:
        tcom.pprint(1, "Unable to generate KCONFIG_FILE")
        return -1

    return 0


# author : LE LURON Pierre
#
# [description]
#
# return value :
#   -1
#    0
def progress_bar(p):
    if p > 100: p = 100
    if p < 0: p = 0
    progress = p/5
    print("\rProgression: [", end="", flush=True)
    for i in range(int(progress)):
        print("#", end="", flush=True)
    for i in range(int(progress), 20):
        print("-", end="", flush=True)
    print("] " + str(int(p)) + "%", end="", flush=True)


# author : LEBRETON Mickael
#
# [description]
#
# return value :
#   -1
#    0
def launcher():
    start_compil_time = time.time()
    install_time = 0
    status = -1
    while status == -1:
        missing_packages = []
        missing_files    = []

        if compilation() == -1:
            start_install_time = time.time()

            if log_analysis(missing_files, missing_packages) == 0:
                if install_missing_packages(missing_files, missing_packages) == 0:
                    tcom.pprint(0, "Restarting compilation")
                    status = -1
                else:
                    status = -3
            else:
                status = -2

            stop_install_time = time.time()
            install_time += stop_install_time - start_install_time
            if (tset.VERBOSE > 1):
                tcom.pprint(3, "TuxML has spent {} to install missing packages".format(time.strftime("%H:%M:%S", time.gmtime(stop_install_time - start_install_time))))
        else:
            status = 0
    end_compil_time = time.time()

    if status == 0:
        compile_time = end_compil_time - start_compil_time - install_time
        duration = time.strftime("%H:%M:%S", time.gmtime(compile_time))
        tcom.pprint(0, "Successfully compiled in {}".format(duration))

        # launching tests
        start_time = time.time()
        status = tbch.boot_try()
        end_time = time.time()
        boot_time = -1
        if status == 0:
            boot_time = end_time - start_time
        else:
            boot_time = status
    else:
        tcom.pprint(1, "Unable to compile using this KCONFIG_FILE, status={}".format(status))

    # sending data to IrmaDB
    cid = tsen.send_data(compile_time, boot_time)
    if cid < 0:
        return -1

    return cid


# author : LEBRETON Mickael
#
# Main function
def main():
    targs.args_handler()

    # init launch
    if init_launcher() != 0:
        sys.exit(-1)

    # launching compilation
    gen_config(tset.KCONFIG)
    tset.BASE_CONFIG_ID = launcher()
    if tset.BASE_CONFIG_ID < 0:
        sys.exit(-1)

    # TODO : sauvegarder les fichiers de compilation dans un autre dossier

    for i in range(0, tset.INCITERS):
        tset.INCREMENTAL_MOD = 1
        tcom.pprint(2, "Launching incremental compilation #" + str(i + 1))
        gen_config()
        if launcher() < 0:
            sys.exit(-1)
        # TODO : charger les fichiers de la compilation base

    sys.exit(0)


# ============================================================================ #


if __name__ == '__main__':
    main()
