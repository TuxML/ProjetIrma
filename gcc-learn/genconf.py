#!/usr/bin/python3

import os
from sys import argv

if len(argv) == 1:
    print("Try: ./genconf.py [Integer]")
    exit(1)

nb = 0
path = "linux-4.13.3"
try:
    nb = int(argv[1])
    if nb <= 0:
        print("You need to enter a non-zero positive integer.")
        exit(1)

except Exception as e:
    print("You need to enter an Integer.")
    print("Try: ./genconf.py [Integer]")
    exit(1)

if not os.path.exists("ConfigFile/"):
    os.makedirs("ConfigFile/")

# Allow to create a given number of config files.
for i in range(nb):
    rc = "KCONFIG_ALLCONFIG= $(pwd)/../core/tuxml.config make -C " + path + " randconfig"
    way = "cp " + path + "/.config ConfigFile/" + str(i) + ".config"
    os.system(rc)
    os.system(way)
