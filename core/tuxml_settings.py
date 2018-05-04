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

## @file tuxml_settings.py
#  @author LEBRETON Mickaël
#  @copyright Apache License 2.0
#  @brief File containing all the tuxml's global variables
#  @details TODO
#  @copyright Apache License, Version 2.0


import sys
import subprocess
import time
import math
import os


## Path to the linux sources
PATH = ""

## Path to the log directory
LOG_DIR = "/logs"

## Path to the standard log file
STD_LOG_FILE = LOG_DIR + "/std.log"

## Path to the error log file
ERR_LOG_FILE = LOG_DIR + "/err.log"

## Path to the tuxml config file
CONF_FILE = PATH + "tuxml.conf"

## Verbose level : 1 = very quiet, 2 = quiet, 3 = chatty, 4 = very chatty
VERBOSE = 3

## Default output is subprocess DEVNULL
OUTPUT          = subprocess.DEVNULL

## Number of cores used by TuxML. By default it uses all the CPU cores
NB_CORES        = 0

## Package manager of the system
PKG_MANAGER     = ""

## Environment details (dictionnary)
TUXML_ENV       = None

## By default we erase the files from the previous compilations
INCREMENTAL_MOD = 0

## Number of incremantal compilations to run
INCITERS        = 0

## Compilation ID of the config on which the incremental compilations are based
BASE_CONFIG_ID  = 0

## Path to the kernel config, used in debug mode and in incrementalVS mod
KCONFIG1        = ""

## Path to the kernel config, used in incrementalVS mod
KCONFIG2        = None

## Colors
COLORS = {
    "white": "\033[0m",              # Default color
    "gray": "\033[38;5;7m",          # Debug
    "black": "\033[38;5;16m",
    "red": "\033[38;5;1m",           # Errors messages
    "light_red": "\033[38;5;9m",
    "green": "\033[38;5;2m",         # Success messages
    "light_green": "\033[38;5;10m",
    "orange": "\033[38;5;3m",        # Warning messages
    "light_orange": "\033[38;5;11m",
    "blue_1": "\033[38;5;4m",
    "light_blue_1": "\033[38;5;12m",
    "blue_2": "\033[38;5;6m",
    "light_blue_2": "\033[38;5;14m",
    "purple": "\033[38;5;5m",
    "light_purple": "\033[38;5;13m"
}

## Virtual machine IP adress
HOST            = "148.60.11.195"

## MySQL user
DB_USER         = "script2"

## MySQL password
DB_PASSWD       = "ud6cw3xNRKnrOz6H"

## MySQL database name (default is IrmaDB_prod)
DB_NAME         = "IrmaDB_"

## SFTP user
SFTP_USER       = "tuxml"

## SFTP password
SFTP_PASSWD     = "ProjetIrma"

## SFTP port
SFTP_PORT       = 22

## SFTP remote directory
SFTP_DIR        = "/var/www/html/files/"

## SFTP local log file
SFTP_LOGS       = "/tmp/tuxml_sftp.log"
