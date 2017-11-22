#!/usr/bin/python3

import os
import time
from sys import argv

# Error if there is no argument "number" of compilation to run.
if len(argv) == 1 or "-h" in argv or "--help" in argv:
    print("")
    print("Try: ./MLfood.py <Integer> [Options]")
    print("")
    print("Options: --no-clean   Do not delete past containers")
    print("         -h, --help    Prompt Options")
    print("         --reset-logs  Delete all the saved logs")
    print("")
    exit(0)

# # We check if the user is a super-user.
# if os.getuid() != 0:
# 	print("You need to have super-user privileges.")
# 	print("")
# 	exit(0)
# We check if the user is a super-user.
if os.getuid() != 0:
    print("You need to have super-user privileges.")
    ar = "sudo"
    for a in argv:
         ar = ar + " {}".format(a)

    os.system(ar)
    exit(0)

# Check if there is the --reset-logs option to erase all the logs.
if "--reset-logs" in argv:
    print("Are-you sure you want to delete all the saved logs? (y/n)")
    reset = input()
    reset.lower()
    if reset == "y":
        print("Deleting all the logs in Logs/...")
        os.system("rm -rf Logs/*")
        print("Delete done.")
        print("")
        exit(0)
    else:
        print("")
        print("Logs are not deleted.")
        print("")
        exit(0)

# Convert the parameter in an Integer which is the number of compilation to do.
# If the number is above 50, the scrypt will ask for a confirmation
try:
    nb = int(argv[1])
    if nb >= 50 :
        print("Are-you sure you want to start " + str(nb) + " compilation? (y/n)")
        ok = input()
        ok.lower()
        if ok != "y":
            print("Canceled")
            exit(0)
except Exception as e:
    print("Please specify a valide number of compilation to launch.")
    print("Command ./MLfood.py <Integer> [Option]")
    exit(0)

# Retrieves the number of compilation to run.
if nb <= 0:
    print("Please enter a non-zero positive integer.")
    exit(0)

# Must contain the list of differents systems images URLs with the execution tuxml script.
images = ["tuxml/tuxmldebian:latest"]

# The image list must not be empty.
if len(images) == 0:
    print("There is no images.")
    exit(0)

# For each url in the url list "images", we run a new docker which run the TuxML command nb times and saves the logs.
for i in range(nb):
    print("")

    # Generation of the logs folder create thanks to the execution date
    today = time.localtime(time.time())
    logsFolder = str(today.tm_year) + str(today.tm_mon) + str(today.tm_mday) + str(today.tm_hour) + str(today.tm_min) + str(today.tm_sec)
    os.system("mkdir -p Logs/" + logsFolder)

    # Get the last version of the image.
    str2 = "sudo docker pull " + images[i % len(images)]
    print("Recuperation dernière version de l'image " + images[i % len(images)])
    os.system(str2)

    # Main command which run a docker which execute the tuxLogs.py script and write the logs in output.logs
    chaine = 'sudo docker run -it ' + images[i % len(images)] + ' /TuxML/tuxLogs.py | tee Logs/' + logsFolder + '/output.logs'
    print("\n=============== Docker n°" + str(i + 1)+ " ===============")
    print(chaine)
    print("==========================================\n")
    os.system(chaine)

    # Get the logs std.logs and err.logs from the last used container.
    dockerid = os.popen("sudo docker ps -lq", "r")
    dock = dockerid.read()
    dock = dock[0:len(dock) -1]
    stdlogs = 'sudo docker cp ' + dock + ':/TuxML/linux-4.13.3/logs/std.logs ./Logs/' + logsFolder
    errlogs = 'sudo docker cp ' + dock + ':/TuxML/linux-4.13.3/logs/err.logs ./Logs/' + logsFolder
    print("Fetch logs to the folder ./Logs/" + logsFolder)
    os.system(stdlogs)
    os.system(errlogs)

    # Clean all the containers used before.
    if not "--no-clean" in argv:
        print("Cleaning containers . . .")
        os.system("sudo docker rm -v $(docker ps -aq)")
        print("Clean done!")
    else:
        print("Option " + argv[2] + " unknown.")
        exit(0)

    print("")

# The end
print("Your tamago... database ate " + str(nb) + " compilation data, come back later to feed him")
print("")
