#!/usr/bin/python3

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
