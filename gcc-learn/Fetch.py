#!/usr/bin/python3

import os
from sys import argv

if len(argv) < 2:
    print("Please, enter a non-zero positive number of core to use")
    print("Try ./Fetch.py [Integer]")
    exit(1)

try:
    n = int(argv[1])

except Exception as e:
    print("You need to give an integer")
    exit(1)
for i in range(100):
        os.system("../core/tuxml.py ../linux-4.13.3 -d ../gcc-learn/config/" + i + ".config -c " + str(n))
