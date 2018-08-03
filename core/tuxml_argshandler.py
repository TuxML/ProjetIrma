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

## @file tuxml_argshandler.py
#  @author LEBRETON Mickaël
#  @copyright Apache License 2.0
#  @brief This file contains the function used to handle tuxml's arguments and
#  parameters


import os
import sys
import subprocess
import argparse
import tuxml_common as tcom
import tuxml_settings as tset
import tuxml_environment as tenv


## @author  LEBRETON Mickaël
#
#  @brief   This function handles the arguments of the ./tuxml.py command
def args_handler():
    msg = "Welcome, this is the TuxML core program.\n\n"

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

    p_help = "path to the Linux source directory"
    v_help = "increase or decrease output verbosity\n"
    v_help += " " * 2 + "1 : very quiet\n"
    v_help += " " * 2 + "2 : quiet\n"
    v_help += " " * 2 + "3 : chatty (default)\n"
    v_help += " " * 2 + "4 : very chatty\n"
    V_help = "display TuxML version and exit"
    d_help = "generate a new kconfig file with the KCONFIG_SEED or use\n"
    d_help = "the KCONFIG_FILE given.\n"
    c_help = "define  the  number  of CPU  cores  to  use  during  the\n"
    c_help += "compilation. By default  TuxML  use all  the  availables\n"
    c_help += "cores on the system."
    i_help = "incremental  mod does  not  erase  files  from  previous\n"
    i_help += "compilations. The I parameter  corresponds to the number\n"
    i_help += "of incremental compilation to launch."
    j_help = "incremental mod with two specifics KCONFIG"
    s_help = "choose on which database send the compilation results"
    t_help = "choose to use the tiny_tuxml.config pre-set file"

    parser = argparse.ArgumentParser(
        description=msg, formatter_class=argparse.RawTextHelpFormatter)
    gexcl1 = parser.add_mutually_exclusive_group()
    parser.add_argument("source_path",     help=p_help)
    parser.add_argument("-v", "--verbose", help=v_help,
                        type=int, choices=range(1, 5))
    parser.add_argument("-V", "--version", help=V_help,
                        action='version', version='%(prog)s pre-alpha v0.2')
    parser.add_argument("-c", "--cores",   help=c_help,
                        type=int, metavar="NB_CORES")
    parser.add_argument("-d", "--debug",   help=d_help,
                        type=str, metavar="KCONFIG")
    gexcl1.add_argument("--incremental",   help=i_help,
                        type=int, metavar="NINC")
    gexcl1.add_argument("--incrementalVS", help=j_help,
                        type=str, metavar="KCONFIG", nargs=2)
    parser.add_argument("--database",      help=s_help,
                        type=str, default='prod', choices=['prod', 'dev'])
    parser.add_argument("--tiny",          help=t_help, action="store_true")
    args = parser.parse_args()

    # ask root credentials
    if os.getuid() != 0:
        sudo_args = ["sudo", sys.executable] + sys.argv + [os.environ]
        os.execlpe('sudo', *sudo_args)
        sys.exit(-1)

    # setting up the database
    tset.DB_NAME += args.database

    if args.tiny:
        tset.TUXCONFIG = "tiny_tuxml.config"

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
    if args.incremental:
        tset.INCITERS = args.incremental
    else:
        # cleaning previous compilation
        tset.INCREMENTAL_MOD = 0
        tcom.pprint(2, "Cleaning previous compilation")
        status = subprocess.call(
            ["make", "-C", tset.PATH, "clean"], stdout=tset.OUTPUT, stderr=tset.OUTPUT)

        if status != 0:
            tcom.pprint(1, "Unable to clean previous compilation")
            sys.exit(-1)

    # handle debug mode
    if args.debug:
        tset.KCONFIG1 = args.debug

    # handle incremental versus mod
    if args.incrementalVS:
        tset.KCONFIG1 = args.incrementalVS[0]
        tset.KCONFIG2 = args.incrementalVS[1]

        print(tset.KCONFIG1, ' ', tset.KCONFIG2, flush=True)

    # set the number of cores
    if args.cores:
        tset.NB_CORES = args.cores
    else:
        try:
            tset.NB_CORES = int(tenv.get_hardware_details()["cpu_cores"])
        except ValueError:
            tcom.pprint(1, "Wrong number of CPU cores value")
            sys.exit(-1)
