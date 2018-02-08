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

# Used to differenciate the Fetch run by users with Fetch called in a docker
# It runs with a different behavior
if "--comp" in argv:
    os.system("../core/tuxml.py ../linux-4.13.3/ -d ConfigFile/" + str(i) + ".config -c " + str(n))
    exit(0)

# Compile all the .config file
for i in range(1):
    print("Docker num " + str(i))
    chaine = 'sudo docker run -it tuxml/tuxmldebian:dev cd /TuxML; echo "cd done"; git pull; git checkout GCC-Learning; echo "checkout done"; cd gcc-learn/; chmod +x Fetch.py; echo "chmod done"; Fetch.py ' + str(n) + ' --comp'
    os.system(chaine)
    print("")
