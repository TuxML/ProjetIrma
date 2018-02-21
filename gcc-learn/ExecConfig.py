#!/usr/bin/python3

import os
from sys import argv

if len(argv) < 3:
	print("Use:")
	print("./ExecConfig.py [num .config] [nb core]")

# Used to differentiate the Fetch run by users with Fetch called in a docker
# It runs with a different behavior
<<<<<<< HEAD
cmd = "../core/tuxml.py ../linux-4.13.3/ -d ConfigFile/" + argv[2] + ".config -c " + argv[1]
=======
cmd = "../tuxml.py ../linux-4.13.3/ -d ConfigFile/" + argv[2] + ".config -c " + argv[1]
>>>>>>> fa8962cb04cf83707371adef1d28c0bb7745389a
os.system(cmd)
exit(0)
