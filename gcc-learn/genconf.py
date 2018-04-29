#!/usr/bin/python3

## @file genconf.py
# @author LE MASLE Alexis
# @copyright Apache License 2.0
# @brief Generate a given number of .config file.
#
# @details You will need linux-4.13.3 kernel folder.
#
#
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
# Script which generate n number of .config files

if len(argv) == 1:
    print("Try: ./genconf.py [Integer]")
    exit(1)

nb = 0 # Number of .config to generate
path = "../linux-4.13.3/" # path where the .config file is
try:
    nb = int(argv[1])
    if nb <= 0:
        print("You need to enter a non-zero positive integer.")
        exit(1)

except Exception as e:
    print("You need to enter an Integer.")
    print("Try: ./genconf.py [Integer]")
    exit(1)

if not os.path.exists("ConfigFile/"):
    os.makedirs("ConfigFile/")

# Allow to create a given number of config files.
for i in range(nb):
    rc = "KCONFIG_ALLCONFIG=$(pwd)/../core/tuxml.config make -C " + path + " randconfig"
    way = "cp " + path + ".config ConfigFile/" + str(i) + ".config"
    os.system(rc)
    os.system(way)
