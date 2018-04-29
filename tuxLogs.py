#!/usr/bin/python3


## @file tuxLogs.py
# @author LE MASLE Alexis
# @copyright Apache License 2.0
# @brief Execute the given number of compilation and incremental compilations by runandlog.py
#
# @details This is the real script call tuxml.py, this is an mid script between runandlog and tuxml use to catch the output from
# tuxml.py, and runandlog.py create the output.log file containing the tuxLogs.py output, composed with tuxml.py and potential crash catchde by tuxLogs.py.

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
import argparse
from sys import argv

# Author Alexis LE MASLE

# Creation of help and argument parser
parser = argparse.ArgumentParser()
parser.add_argument("incremental", help = "The incremental factor (0 by default)", type=int, nargs='?', default=0)
args = parser.parse_args()

# Run tuxml.py and retrieves the output converted in a log file.
print("")
print('Starting tuxml.py ...')
print("")
chaine = '/TuxML/tuxml.py /TuxML/linux-4.13.3 -v 4 --incremental ' + str(args.incremental)
print("")
os.system(chaine)
