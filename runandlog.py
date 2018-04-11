#!/usr/bin/python3

import os
import argparse
from sys import argv

# Author Alexis LE MASLE

# Creation of help and argument parser
parser = argparse.ArgumentParser()
parser.add_argument("incremental", help = "The incremental factor (0 by default)", type=int, nargs='?', default=0)
args = parser.parse_args()

# Run tuxLogs.py and retrieves the output converted in a log file.
print("")
print('Running tuxLogs.py ...')
print("")
chaine = '/TuxML/tuxLogs.py ' + str(args.incremental) + ' | tee output.log'
print("")
os.system(chaine)
