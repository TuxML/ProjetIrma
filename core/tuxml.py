#!/usr/bin/python3

import os
import sys
import subprocess
import re
import shutil
import time
import argparse
import curses
import tuxml_sendDB as tsen
import tuxml_common as tcom
import tuxml_settings as tset
import tuxml_depman as tdep
import tuxml_environment as tenv


# author : LEBRETON Mickael
#
# This function handles the arguments of the ./tuxml.py command
def args_handler():
    msg  = "Welcome, this is the TuxML core program.\n\n"

    msg += "The goal of TuxML is to  automatically  compile Linux kernel sources in order to\n"
    msg += "build a database for a machine learning algorithm.\n"
    msg += "If the compilation crashes, TuxML  analyzes the error log file  to determine the\n"
    msg += "causes. There are two possible ways:\n"
    msg += "  * it is a missing  package : TuxML will install it and  resume the compilation\n"
    msg += "  * the error can't be fixed : the compilation stops\n"
    msg += "Then TuxML sends the results of the compilation to the database.\n\n"

    msg += "Keep in mind that the program is currently  in developpement stage. Please visit\n"
    msg += "our Github at <https://github.com/TuxML> in order to report any issue.\n"
    msg += "Thanks !\n\n"

    p_help  = "path to the Linux source directory"
    v_help  = "increase or decrease output verbosity\n"
    v_help += " " * 2 + "1 : very quiet\n"
    v_help += " " * 2 + "2 : quiet\n"
    v_help += " " * 2 + "3 : chatty (default)\n"
    v_help += " " * 2 + "4 : very chatty\n"
    V_help  = "display TuxML version and exit"
    d_help  = "debug a given KCONFIG_SEED  or  KCONFIG_FILE. If no seed\n"
    d_help += "or file are  given, the script  will  use  the  existing\n"
    d_help += "KCONFIG_FILE in the linux source directory"
    c_help  = "define  the  number  of CPU  cores  to  use  during  the\n"
    c_help += "compilation. By default  TuxML  use all  the  availables\n"
    c_help += "cores on the system."
    i_help  = "incremental  mod does  not  erase  files  from  previous\n"
    i_help += "compilations. The CID correspond to the ID of the origi-\n"
    i_help += "nal compilation."
    s_help  = "choose on which database send the compilation results"

    parser = argparse.ArgumentParser(description=msg, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("source_path",     help=p_help)
    parser.add_argument("-v", "--verbose", help=v_help, type=int, choices=range(1,5))
    parser.add_argument("-V", "--version", help=V_help, action='version', version='%(prog)s pre-alpha v0.2')
    parser.add_argument("-c", "--cores",   help=c_help, type=int, metavar="NB_CORES")
    parser.add_argument("-d", "--debug",   help=d_help, type=str, metavar="KCONFIG", nargs='?', const=-1)
    parser.add_argument("--inc-mod",       help=i_help, type=int, metavar="CID")
    parser.add_argument("--database",      help=s_help, type=str, default='prod', choices=['prod', 'dev'])
    args = parser.parse_args()

    # ask root credentials
    if os.getuid() != 0:
        sudo_args = ["sudo", "-k", sys.executable] + sys.argv + [os.environ]
        os.execlpe('sudo', *sudo_args)
        sys.exit(-1)

    # setting up the database
    tset.DB_NAME += args.database

    # manage level of verbosity
    if args.verbose:
        tset.VERBOSE = args.verbose

        if tset.VERBOSE > 3:
            tset.OUTPUT = sys.__stdout__
    else:
        tset.VERBOSE = 3

    # store the linux source path in a global var
    if not os.path.exists(args.source_path):
        tcom.pprint(1, "This path doesn't exist")
        sys.exit(-1)
    else:
        tset.PATH = args.source_path

    # enable or disable incremental mod (clean or not clean, that's the question)
    if args.inc_mod:
        tset.INCREMENTAL_MOD = 1
        tset.CONFIG_ID = args.inc_mod
    else:
        # cleaning previous compilation
        tset.INCREMENTAL_MOD = 0
        tcom.pprint(2, "Cleaning previous compilation")
        status = subprocess.call(["make", "-C", tset.PATH, "mrproper"], stdout=tset.OUTPUT, stderr=tset.OUTPUT)

        if status != 0:
            tcom.pprint(1, "Unable to clean previous compilation")
            sys.exit(-1)

    # handle debug mode
    if args.debug:
        if args.debug == -1:
            # use previous config file
            if not os.path.exists(tset.PATH + "/.config"):
                tcom.pprint(1, "KCONFIG_FILE not found")
                sys.exit(-1)
            else:
                tcom.pprint(2, "Using previous KCONFIG_FILE")
        else:
            # debug config with given KCONFIG_SEED
            try:
                kconfig_seed = int(args.debug, 16)
            except ValueError:
                kconfig_seed = -1

            if kconfig_seed != -1:
                tcom.pprint(2, "Generating config file with KCONFIG_SEED=" + args.debug)
                status = subprocess.call(["KCONFIG_SEED=" + args.debug + " make -C " + tset.PATH + " randconfig"], stdout=tset.OUTPUT, stderr=tset.OUTPUT, shell=True)

                if status != 0:
                    tcom.pprint(1, "Unable to generate KCONFIG_FILE")
                    sys.exit(-1)
            else:
                # debug config with given KCONFIG_FILE
                if os.path.exists(args.debug):
                    tcom.pprint(2, "Using KCONFIG_FILE " + args.debug)
                    shutil.copyfile(args.debug, tset.PATH + "/.config") # TODO maybe a better way ?
                else:
                    tcom.pprint(1, "Invalid KCONFIG_SEED or KCONFIG_FILE doesn't exist")
                    sys.exit(-1)
    else:
        # generating new KConfig file
        tcom.pprint(2, "Randomising new KCONFIG_FILE")
        status = subprocess.call(["KCONFIG_ALLCONFIG=" + os.path.dirname(os.path.abspath(__file__)) + "/tuxml.config make -C " + tset.PATH + " randconfig"], stdout=tset.OUTPUT, stderr=tset.OUTPUT, shell=True)

        if status != 0:
            tcom.pprint(1, "Unable to generate KCONFIG_FILE")
            sys.exit(-1)

    # set the number of cores
    if args.cores:
        tset.NB_CORES = args.cores
    else:
        try:
            tset.NB_CORES = int(tenv.get_hardware_details()["cpu_cores"])
        except ValueError:
            tcom.pprint(1, "Wrong number of CPU cores value")
            sys.exit(-1)


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


# author : LEBRETON Mickael
#
# Main function
def main():
    args_handler()

    # get environment details
    tset.TUXML_ENV = tenv.get_environment_details()

    # get the package manager
    tset.PKG_MANAGER = tcom.get_package_manager()
    if tset.PKG_MANAGER == None:
        sys.exit(-1)

    # updating package database
    if tcom.update_system() != 0:
        sys.exit(-1)

    # install default packages
    if tdep.install_default_dependencies() != 0:
        sys.exit(-1)

    # launching compilation
    start_compil_time   = time.time()
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
        status = end_compil_time - start_compil_time - install_time
        compile_time = time.strftime("%H:%M:%S", time.gmtime(status))
        tcom.pprint(0, "Successfully compiled in {}".format(compile_time))
        # TODO kernel tests
    else:
        tcom.pprint(1, "Unable to compile using this KCONFIG_FILE, status={}".format(status))

    # sending data to IrmaDB
    if tsen.send_data(status) != 0:
        sys.exit(-1)

    sys.exit(0)


# ============================================================================ #


if __name__ == '__main__':
    main()
