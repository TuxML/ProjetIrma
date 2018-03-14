#!/usr/bin/python3

import os
from sys import argv

# Author Alexis LE MASLE

if "--dev" in argv:
    # Update the image to the latest dev version
    print('Retrieves latest version of TuxML scritps...')
    os.system('cd /TuxML/')
    os.system('git pull')
    os.system('git checkout dev')

incr = 1

if len(argv) == 3:
    incr = int(argv[2])

# Run tuxml.py and retrieves the output converted in a log file.
print('Starting tuxml.py ...')
os.system('/TuxML/tuxml.py /TuxML/linux-4.13.3 -v 4 --incremental ' + incr )
