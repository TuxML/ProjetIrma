import sys
import time
import math

# ===== GLOBALS =====
# "/std_{}.logs".format(math.ceil(time.time()))
# "/err_{}.logs".format(math.ceil(time.time()))
PATH = ""
LOG_DIR = "/logs"
STD_LOG_FILE = LOG_DIR + "/std.logs"
ERR_LOG_FILE = LOG_DIR + "/err.logs"
DEBUG = False
OUTPUT = sys.__stdout__
