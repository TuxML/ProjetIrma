#!/usr/bin/python3

## @file ExecConfig.py
# @author LE MASLE Alexis
# @copyright Apache License 2.0
# @brief File which start tuxml.py with specific parameters
#
# @details This script works almost like tuxLogs.py, it is used to execute tuxml.py with the number of cores given by Fetch.py.
# The program runs tuxml.py with a given number of cores, and configure it to send the compilations data to an other database used
# to make correlations as it was said in Fetch.py with the help of Machine Learning.

# ExecConfig.py, Fetch.py and genconf.py are NOT USEFULL in the TuxML Project.

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
cmd = "/TuxML/tuxml.py /TuxML/linux-4.13.3/ -d /TuxML/gcc-learn/" + argv[1] + ".config -c " + argv[2] + " -v 4 --database alexis --incremental 0"
os.system(cmd)
