#!/usr/bin/python3

import os
from sys import argv

# Author Alexis LE MASLE

if len(argv) < 3:
	print("Use:")
	print("./ExecConfig.py [num .config] [nb core]")
	exit(0)

# It runs with a different behavior
cmd = "./tuxml.py linux-4.13.3/ -d gcc-learn/" + argv[2] + ".config -c " + argv[1]
os.system(cmd)
