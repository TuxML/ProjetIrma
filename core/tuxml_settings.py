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
