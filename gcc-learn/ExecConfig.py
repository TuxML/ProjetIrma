#!/usr/bin/python3

import os
from sys import argv

# Used to differenciate the Fetch run by users with Fetch called in a docker
# It runs with a different behavior
cmd = "../core/tuxml.py ../linux-4.13.3/ -d ConfigFile/" + argv[2] + ".config -c " + argv[1]
os.system(cmd)
exit(0)
