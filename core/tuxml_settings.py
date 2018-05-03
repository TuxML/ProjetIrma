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

import sys
import subprocess
import time
import math
import os

# GLOBALS
## MISC
PATH            = ""                       # Path to the linux sources
LOG_DIR         = "/logs"                  # Path to the log directory
STD_LOG_FILE    = LOG_DIR + "/std.log"     # Path to the standard log file
ERR_LOG_FILE    = LOG_DIR + "/err.log"     # Path to the error log file
CONF_FILE       = PATH + "tuxml.conf"
VERBOSE         = 1                        # Verbose level (0 = Quiet, 1 = normal, 2 = chatty)
OUTPUT          = subprocess.DEVNULL       # Default output
NB_CORES        = 0                        # Number of cores used by TuxML
PKG_MANAGER     = ""                       # Package manager of the system
TUXML_ENV       = None                     # Environment details
INCREMENTAL_MOD = 0                        # By default we don't use the files from the previous compilations
INCITERS        = 0                        # Config ID on which run the incremental tests
BASE_CONFIG_ID  = 0
KCONFIG1        = None
KCONFIG2        = None

## COLORS
WHITE           = "\033[0m"                # Default color
GRAY            = "\033[38;5;7m"           # Debug
BLACK           = "\033[38;5;16m"
RED             = "\033[38;5;1m"           # Errors messages
LIGHT_RED       = "\033[38;5;9m"
GREEN           = "\033[38;5;2m"           # Success messages
LIGHT_GREEN     = "\033[38;5;10m"
ORANGE          = "\033[38;5;3m"           #
LIGHT_ORANGE    = "\033[38;5;11m"
BLUE_1          = "\033[38;5;4m"
LIGHT_BLUE_1    = "\033[38;5;12m"
BLUE_2          = "\033[38;5;6m"
LIGHT_BLUE_2    = "\033[38;5;14m"
PURPLE          = "\033[38;5;5m"
LIGHT_PURPLE    = "\033[38;5;13m"

## REMOTE ACCESS
HOST            = "148.60.11.195"
### DATABASE
DB_USER         = "script2"
DB_PASSWD       = "ud6cw3xNRKnrOz6H"
DB_NAME         = "IrmaDB_"
### SFTP
SFTP_USER       = "tuxml"
SFTP_PASSWD     = "ProjetIrma"
SFTP_PORT       = 22
SFTP_DIR        = "/var/www/html/files/"
SFTP_LOGS       = "/tmp/tuxml_sftp.log"
