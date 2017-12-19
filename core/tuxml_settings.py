import sys
import subprocess
import time
import math
import os

# ===== GLOBALS =====
PATH = ""
LOG_DIR = "/logs"
STD_LOG_FILE = LOG_DIR + "/std.log"
ERR_LOG_FILE = LOG_DIR + "/err.log"
VERBOSE = 0
OUTPUT = subprocess.DEVNULL
NB_CORES = 0
PKG_MANAGER = ""
TUXML_ENV = None, None, None
INCREMENTAL_MOD = False
