#!/usr/bin/python3

import os
from sys import argv


# Error if there is no argument "number" of compilation to run.
if len(argv) == 1 :
    print("Please specify a number of compilation to launch.")
    print("Command ./MLfood.py [Integer]")
    exit()

# Convert the parameter in an Integer which is the number of compilation to do.
# If the number is above 50, the scrypt will ask for a confirmation
try:
    nb = int(argv[1])
    if nb >= 50 :
        print("Are-you sure you want to start {} compilation? (y/n)".format(nb))
        ok = input()
        ok.lower()
        if ok != "y":
            print("Canceled")
            exit()

except Exception as e:
    print("Please specify a valide number of compilation to launch.")
    print("Command ./MLfood.py [Integer]")
    exit()

# Retrieves the number of compilation to run.
if nb <= 0:
    print("Please enter a non-zero positive integer.")
    exit()

# Must contain the list of differents systems images URLs with the execution tuxml script.
images = ["tuxml/tuxmldebian:latest"]

# The image list must not be empty.
if len(images) == 0:
    print("There is no images.")
    exit()

# For each url in the url list "images", we run a new docker which run the TuxML command nb times.
# For each tuxml.py, logs are saved in the Logs/Tuxml-[nb]/
for i in range(nb):
    folder_name = "Tuxml-{}".format(i)
    os.system("mkdir -p Logs/{}".format(folder_name))
    str2 = "sudo docker pull {} ".format(images[i % len(images)])
    print("Recuperation dernière version de l'image {}".format(images[i % len(images)]))
    os.system(str2)
    chaine = 'sudo docker run -it {} /TuxML/tuxLogs.py'.format(images[i % len(images)])
    print("\n=============== Docker n°{} ===============".format(i+1))
    print(chaine)
    print("==========================================\n")
    os.system(chaine)

    dockerid = os.popen("sudo docker ps -lq", "r")
    dock = dockerid.read()
    dock = dock[0:len(dock) -1]
    tuxmllogs = 'sudo docker cp {}:/TuxML/Logs/tuxML.logs ./Logs/{}'.format(dock, folder_name)
    stdlogs = 'sudo docker cp {}:/TuxML/Logs/std.logs ./Logs/{}'.format(dock, folder_name)
    errlogs = 'sudo docker cp {}:/TuxML/Logs/err.logs ./Logs/{}'.format(dock, folder_name)

    print("Recovery of logs in the folder ./Logs/{}".format(folder_name))
    os.system(tuxmllogs)
    os.system(stdlogs)
    os.system(errlogs)
    # print(dock)  # The ID of the current container
    # print(tuxmllogs)  # Print the cp command of tuxml.logs
    # print(stdlogs)    # Print the cp command of std.logs
    # print(errlogs)    # Print the cp command of err.logs
    print("")
