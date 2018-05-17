#!/usr/bin/python3

## @file Fetch.py
# @author LE MASLE Alexis
# @copyright Apache License 2.0
# @brief File used to start a given number of compilation with a given number of core
#
# @details This file was created to gain data on specific parameters of compilations, here it is used to
# perform a compilation on several machine where each one compile with a different number of cores, genconf.py has been used to
# generate 100 .config, all the machine will run tuxml.py with a different number of cores on the same 100 .config.
# With this, we can make some calculation and predictions on what would be the behavior to compile a .config file with 1 core and an
# 4 core. The objective is to see is there are correlations between options in the Linux Kernel or if an other factor than hardware
# affect compilations.
# All machine used to perform the same .config needs to be the same ( Same configurations, hardware ).

# ExecConfig.py, Fetch.py and genconf.py are NOT USEFUL in the TuxML Project.

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

import subprocess
from sys import argv

# Author Alexis LE MASLE

if len(argv) < 2:
    print("Please, enter a non-zero positive number of core to use")
    print("Try ./Fetch.py [Integer]")
    exit(0)

try:
    n = int(argv[1])

except Exception as e:
    print("You need to give an integer")
    exit(0)

print("Retrieves last image...")
subprocess.run("sudo docker pull tuxml/tuxmldebian:dev", shell=True).stdout

# Compile all the .config file
for i in range(100):
    print("------Docker num " + str(i) + "-------")
    chaine = 'sudo docker run -i tuxml/tuxmldebian:dev TuxML/gcc-learn/ExecConfig.py ' + str(i) + ' ' + str(n)
    subprocess.run(chaine, shell=True).stdout
    print("-------------------------")
    print("Cleaning containers . . .")
    subprocess.run("sudo docker rm -v $(sudo docker ps -aq)", shell=True).stdout
    print("Clean done!")
    print("")
