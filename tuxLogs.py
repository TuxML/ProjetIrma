#!/usr/bin/python3

import os
from sys import argv

# Author Alexis LE MASLE

if len(argv) == 1 or "-h" in argv or "--help" in argv:
    print("Try: ./ExecConfig.py <Integer>")
    print("<Integer> is the incremental factor ( 0 by default )")
    print("-h, --help       Display help")
    print("")
    exit(0)


# if "--dev" in argv:
#     # Update the image to the latest dev version
#     print('Retrieves latest version of TuxML scritps...')
#     os.system('cd /TuxML/')
#     os.system('git checkout dev')
#     os.system('git pull')

incr = 0

if len(argv) == 3:
    incr = int(argv[2])

# Run tuxml.py and retrieves the output converted in a log file.
print("")
print('Starting tuxml.py ...')
print("")
os.system('/TuxML/tuxml.py /TuxML/linux-4.13.3 -v 4 --incremental ' + incr )
