#!/usr/bin/python3

import os
import sys
import subprocess
import re
import shutil
import time
import argparse
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
        pkgs = tdep.build_dependencies_arch(missing_files);
    elif distro == 1:
        pkgs = tdep.build_dependencies_debian(missing_files);
    elif distro == 2:
        pkgs = tdep.build_dependencies_redhat(missing_files);
    else:
        pass

    pkg_manager = tcom.get_package_manager()
    if pkg_manager == None:
        return -3

    if tcom.update_system(pkg_manager) != 0:
        return -2

    if tcom.install_packages(pkg_manager, pkgs + missing_packages) != 0:
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
                if len(line.split(":")) == 4:
                    # case "/bin/sh: 1: <command>: not found"
                    missing_files.append(line.split(":")[2])
                else:
                    # ./scripts/gcc-plugin.sh: 11: ./scripts/gcc-plugin.sh: <package>: not found
                    missing_packages.append(line.split(":")[3])
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


# author : LEBRETON Mickael
#
# [args_handler description]
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
    msg += "our Github at https://github.com/TuxML in order to report any issue.\n"
    msg += "Thanks !\n\n"

    p_help  = "path to the Linux source directory"
    v_help  = "increase output verbosity"
    V_help  = "display TuxML version and exit"
    d_help  = "debug a given  kconfig seed. If no seed is given, TuxML\n"
    d_help += "will use the existing kconfig file in  the linux source\n"
    d_help += "directory"

    parser = argparse.ArgumentParser(description=msg, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("source_path",     help=p_help)
    parser.add_argument("-v", "--verbose", help=v_help, action="store_true")
    parser.add_argument("-V", "--version", help=V_help, action='version', version='%(prog)s pre-alpha v0.2')
    parser.add_argument("-d", "--debug",   help=d_help, type=str, metavar="KCONFIG_SEED", nargs='?', const=-1)
    args = parser.parse_args()

    # ask root credentials
    if os.getuid() != 0:
          sudo_args = ["sudo", "-k", sys.executable] + sys.argv + [os.environ]
          os.execlpe('sudo', *sudo_args)
          sys.exit(-1)

    # manage level of verbosity
    if args.verbose:
        tset.VERBOSE  = True
        tset.OUTPUT = sys.__stdout__
        date = time.strftime("%H:%M:%S", time.gmtime(time.time()))
    else:
        tset.VERBOSE  = False
        tset.OUTPUT = subprocess.DEVNULL

    # store the linux source path in a global var
    if not os.path.exists(args.source_path):
        tcom.pprint(1, "This path doesn't exist")
        sys.exit(-1)
    else:
        tset.PATH = args.source_path

    if args.debug:
        if args.debug == -1:
            # use previous config file
            if not os.path.exists(tset.PATH + "/.config"):
                tcom.pprint(1, "KConfig file not found")
                sys.exit(-1)
            else:
                tcom.pprint(2, "Using previous kconfig file")
        else:
            # generating config file with given seed
            try:
                int(args.debug, 16);
            except ValueError:
                tcom.pprint(1, "Invalid KCONFIG_SEED")
                sys.exit(-1)

            tcom.pprint(2, "Generating config file with KCONFIG_SEED=" + args.debug)
            output = subprocess.call(["KCONFIG_SEED=" + args.debug + " make -C " + tset.PATH + " randconfig"], stdout=tset.OUTPUT, stderr=tset.OUTPUT, shell=True)
    else:
        # cleaning previous compilation and generating new KConfig file
        tcom.pprint(2, "Cleaning previous compilation")
        subprocess.call(["make", "-C", tset.PATH, "mrproper"], stdout=tset.OUTPUT, stderr=tset.OUTPUT)

        tcom.pprint(2, "Randomising new config file")
        output = subprocess.call(["KCONFIG_ALLCONFIG=" + os.path.dirname(os.path.abspath(__file__)) + "/tuxml.config make -C " + tset.PATH + " randconfig"], stdout=tset.OUTPUT, stderr=tset.OUTPUT, shell=True)


# author : LEBRETON Mickael
#
# [main description]
def main():
    args_handler()

    # install default packages
    if tdep.install_default_dependencies() != 0:
        sys.exit(-1)

    # launching compilation
    start_time = time.time()
    status = -1
    while status == -1:
        status = compile()
    end_time = time.time()

    # testing kernel
    if status == 0:
        tcom.pprint(0, "Testing the kernel config")
        status = end_time - start_time
        compile_time = time.strftime("%H:%M:%S", time.gmtime(status))
        tcom.pprint(0, "Successfully compiled in {}, sending data".format(compile_time))
    else:
        # status == -2
        tcom.pprint(1, "Unable to compile using this config or another error happened, sending data anyway")

    # sending data to IrmaDB
    # tsen.send_data(tset.PATH, tset.ERR_LOG_FILE, status)


# ============================================================================ #


if __name__ == '__main__':
    main()
