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

incr = 0
if len(argv) == 2:
    try:
        incr = int(argv[1])
    except Exception as e:
        print("Param", "\"" + argv[1] + "\"", "ignored. ( Not an valid Integer, see --help to know more. )")

# Run tuxml.py and retrieves the output converted in a log file.
print("")
print('Starting tuxml.py ...')
print("")
chaine = '/TuxML/tuxml.py /TuxML/linux-4.13.3 -v 4 --incremental ' + str(incr)
print("")
os.system(chaine)
