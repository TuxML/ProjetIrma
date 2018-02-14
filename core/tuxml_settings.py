import sys
import subprocess
import time
import math
import os

# ===== GLOBALS =====
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

WHITE           = "\033[0m"                # Default
GRAY            = "\033[38;5;7m"
BLACK           = "\033[38;5;16m"
RED             = "\033[38;5;1m"           # Success
LIGHT_RED       = "\033[38;5;9m"
GREEN           = "\033[38;5;2m"           # Error
LIGHT_GREEN     = "\033[38;5;10m"
ORANGE          = "\033[38;5;3m"           # Warning
LIGHT_ORANGE    = "\033[38;5;11m"
BLUE_1          = "\033[38;5;4m"
LIGHT_BLUE_1    = "\033[38;5;12m"
BLUE_2          = "\033[38;5;6m"
LIGHT_BLUE_2    = "\033[38;5;14m"
PURPLE          = "\033[38;5;5m"
LIGHT_PURPLE    = "\033[38;5;13m"
