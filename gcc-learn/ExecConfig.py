#!/usr/bin/python3

import os
from sys import argv

# Author Alexis LE MASLE

## COLORS
WHITE           = "\033[0m"                # Default color
GRAY            = "\033[38;5;7m"           # Debug
BLACK           = "\033[38;5;16m"
RED             = "\033[38;5;1m"           # Errors messages
LIGHT_RED       = "\033[38;5;9m"
GREEN           = "\033[38;5;2m"           # Success messages
LIGHT_GREEN     = "\033[38;5;10m"
ORANGE          = "\033[38;5;3m"
LIGHT_ORANGE    = "\033[38;5;11m"
BLUE_1          = "\033[38;5;4m"
LIGHT_BLUE_1    = "\033[38;5;12m"
BLUE_2          = "\033[38;5;6m"
LIGHT_BLUE_2    = "\033[38;5;14m"
PURPLE          = "\033[38;5;5m"
LIGHT_PURPLE    = "\033[38;5;13m"

if len(argv) < 3:
	print("")
	print(LIGHT_BLUE_1 + "Use:")
	print("./ExecConfig.py [num .config] [nb core]" + GRAY)
	print("")
	exit(0)

if int(argv[2]) <= 0:
	print(RED + "Please enter a non zero positive number of core." + GRAY)
	exit(0)

# It runs with a different behavior
cmd = "/TuxML/tuxml.py /TuxML/linux-4.13.3/ -d /TuxML/gcc-learn/" + argv[1] + ".config -c " + argv[2]
os.system(cmd)
