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

print("Retrieves last image...")
os.system("sudo docker pull tuxml/tuxmldebian:dev")
	
# Compile all the .config file
for i in range(1):
    print("Docker num " + str(i))
    chaine = 'sudo docker run -it tuxml/tuxmldebian:dev /TuxML/gcc-learn/ExecConfig.py ' + str(n) + ' ' + str(i)
    os.system(chaine)
    print("")
