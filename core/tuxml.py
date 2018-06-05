#!/usr/bin/python3

# -*- coding: utf-8 -*-

#   Copyright 2018 TuxML Team
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

## @file tuxml.py
#  @author LEBRETON Mickaël
#  @copyright Apache License 2.0
#  @brief Tuxml's main file, containing the init function, the launcher etc


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


## @author  LEBRETON Mickaël
#
#  @brief   This function installs the missing packages
#  @details First build the  dependencies by trying to associate a package to a
#  missing file. Then install all the missing packages.
#
#  @param   missing_files List of missing files whose you want to associate to a
#  package
#  @param   missing_packages List of missing packages you want to install
#
#  @returns -1 Package(s) not found
#  @returns  0 Successfull installation
def install_missing_packages(missing_files, missing_packages):
    if tdep.build_dependencies(missing_files, missing_packages) != 0:
        return -1

    if tcom.install_packages(missing_packages) != 0:
        return -1

    return 0


## @author  LEBRETON Mickaël
#
#  @brief   Analyzes the error log file and try to find the missing packages and
#  files
#  @details The analysis is based on regular expressions, we search for the following
#  patterns : "fatal error", "command not found", "not found". Those give missing
#  files and missing packages. Following the pattern we append the data to one of
#  the two list given as parameters.
#
#  @param   missing_files The list of missing files (empty at the beginning)
#  @param   missing_packages The list of missing packages (empty at the beginning)
#
#  @returns -1 the program wasn't able to find the missing package(s)
#  @returns  0 the program was able to find the missing package(s)
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


## @author  LE LURON Pierre
#
#  @brief   Display a progress bar (not used currently)
#
#  @param   p The current progression (between 0 and 100)
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
    if p == 100:
        print("\n")


## @author  LEBRETON Mickaël
#
#  @brief   Start the compilation and redirect the logs to std.log and err.log
#
#  @returns -1 compilation has failed
#  @returns  0 no error
#
#  @todo loading bar [ ##########-------------------- ] 33%
def compilation():
    tcom.pprint(2, "Compilation in progress")

    if not os.path.exists(tset.PATH + tset.LOG_DIR):
        os.makedirs(tset.PATH + tset.LOG_DIR)

    with open(tset.PATH + tset.STD_LOG_FILE, "w") as std_logs, open(tset.PATH + tset.ERR_LOG_FILE, "w") as err_logs:
        status = subprocess.call("make -C tset.PATH -j" + str(tset.NB_CORES) + " | ts -s", shell=True stdout=std_logs, stderr=err_logs)

    if status == 0:
        tcom.pprint(0, "Compilation done")
        return 0
    else:
        tcom.pprint(2, "Compilation failed, exit status : {}".format(status))
        return -1


## @author  LEBRETON Mickaël
#
#  @brief   Init the environment compilation, the package manager, update the system
#  and install default dependencies.
#
#  @returns -3 failed to installed default dependencies
#  @returns -2 failed to update system
#  @returns -1 package manager not found
#  @returns  0 no error
def init_launcher():
    # get environment details
    tset.TUXML_ENV = tenv.get_environment_details()

    # get the package manager
    tset.PKG_MANAGER = tcom.get_package_manager()
    if tset.PKG_MANAGER is None:
        return -1

    # updating package database
    if tcom.update_system() != 0:
        return -2

    # install default packages
    if tdep.install_default_dependencies() != 0:
        return -3

    return 0


## @author  LEBRETON Mickaël
#
#  @brief   Generate the kconfig file
#  @details If the Kconfig parameter is empty, tuxml will randomize a new kconfig.
#  Else it will check if the parameter is a hexadecimal number (seed format) or a
#  path. If it's one or  the other it will generate or use the associate kconfig
#  file.
#
#  @param   Kconfig Kconfig given as a seed or a path to an existing config file (optional)
#
#  @returns -1 Unable to generate or used the kconfig file
#  @returns  0 No error
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
                shutil.copyfile(Kconfig, tset.PATH + "/.config")
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


## @author  LEBRETON Mickaël
#
#  @brief   Launch the compilation
#  @details Start a clock a the beginning of the loop. If the compilation failed
#  we start the log analysis and we try to install the missing packages. We loop
#  as long as status value is -1, it means  we found  missing packages. Else, if
#  status is -2 (log analysis failed)  or  -3 (installation failed)  we stop the
#  loop. Once the compilation is complete (status is 0), we can launch boot test
#  on the kernel. Then  send  all the  results (compilation time  and  boot test
#  time) to the database.
#
#  @returns -1 Failed to send results to the database
#  @returns >0 The compilation ID
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
                tcom.pprint(2, "TuxML has spent {} to install missing packages".format(time.strftime("%H:%M:%S", time.gmtime(stop_install_time - start_install_time))))
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
        compile_time = status
        boot_time = -1
        tcom.pprint(1, "Unable to compile using this KCONFIG_FILE, status={}".format(status))

    # sending data to IrmaDB
    cid = tsen.send_data(compile_time, boot_time)
    if cid <= 0:
        return -1

    return cid


## @author  LEBRETON Mickaël
#
#  @brief   Main function
#  @details Init the launcher then start an initial compilation (base config).
#  If the incremental mod is ON, we launch INCITERS compilations.
#
#  @todo When using incremental mod save the base config files in an other folder
#  then load them before all new incremental compilation.
def main():
    targs.args_handler()

    # init launch
    if init_launcher() != 0:
        sys.exit(-1)

    # launching compilation
    gen_config(tset.KCONFIG1)
    tset.BASE_CONFIG_ID = launcher()
    if tset.BASE_CONFIG_ID < 0:
        sys.exit(-1)

    if tset.KCONFIG2:
        tset.INCREMENTAL_MOD = 1
        gen_config(tset.KCONFIG2)
        if launcher() < 0:
            sys.exit(-1)
        sys.exit(0)

    cid_array = []
    for i in range(0, tset.INCITERS):
        tset.INCREMENTAL_MOD = 1
        tset.TUXML_ENV["compilation"]["incremental_mod"] = "1"
        tcom.pprint(0, "Launching incremental compilation #" + str(i + 1))
        gen_config()

        tmp_cid = launcher()
        if tmp_cid < 0:
            sys.exit(-1)
        cid_array.append(tmp_cid)

    tcom.pprint(0, "DATABASE CONFIGURATION ID={}".format(tset.BASE_CONFIG_ID))

    for c in range(len(cid_array)):
        tcom.pprint(0, "INCREMENTAL CONFIGURATION ID #{}={}".format(c, cid_array[c]))

    sys.exit(0)


# ============================================================================ #


if __name__ == '__main__':
    main()
