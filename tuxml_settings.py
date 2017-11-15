import sys
import time
import math

# ===== GLOBALS =====
PATH = ""
LOG_DIR = "/logs"
STD_LOG_FILE = LOG_DIR + "/std_{}.logs".format(math.ceil(time.time()))
ERR_LOG_FILE = LOG_DIR + "/err_{}.logs".format(math.ceil(time.time()))
DEBUG = False
OUTPUT = sys.__stdout__
