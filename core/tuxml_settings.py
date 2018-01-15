import sys
import subprocess
import time
import math
import os

# ===== GLOBALS =====
PATH = ""                               # Path to the linux sources
LOG_DIR = "/logs"                       # Path to the log directory
STD_LOG_FILE = LOG_DIR + "/std.log"     # Path to the standard log file
ERR_LOG_FILE = LOG_DIR + "/err.log"     # Path to the error log file
VERBOSE = 1                             # Verbose level (0 = Quiet, 1 = normal, 2 = chatty)
OUTPUT = subprocess.DEVNULL             # Default output
NB_CORES = 0                            # Number of cores used by TuxML
PKG_MANAGER = ""                        # Package manager of the system
TUXML_ENV = None                        # Environment details
INCREMENTAL_MOD = False                 # By default we don't use the files from the previous compilations
