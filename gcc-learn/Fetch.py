#!/usr/bin/python3

import os
from sys import argv

# Author Alexis LE MASLE

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
    print("------Docker num " + str(i) + "-------")
    chaine = 'sudo docker run -t tuxml/tuxmldebian:dev "cd TuxML/gcc-learn; ./ExecConfig.py ' + str(n) + ' ' + str(i) + ' "'
    os.system(chaine)
    print("-------------------------")
    print("Cleaning containers . . .")
    os.system("sudo docker rm -v $(sudo docker ps -aq)")
    print("Clean done!")
    print("")
