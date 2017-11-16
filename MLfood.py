#!/usr/bin/python3

import os
import time
from sys import argv

# Error if there is no argument "number" of compilation to run.
if len(argv) == 1 or "-h" in argv or "--help" in argv:
    print("")
    print("Try: ./MLfood.py <Integer> [Options]")
    print("")
    print("Options: -c, --clean   Delete past containers")
    print("         -h, --help    Prompt Options")
    print("")
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
    print("Command ./MLfood.py <Integer> [Option]")
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

# For each url in the url list "images", we run a new docker which run the TuxML command nb times and saves the logs.
for i in range(nb):
    print("")

    # Generation of the logs folder create thanks to the execution date
    today = time.localtime(time.time())
    logsFolder = str(today.tm_year) + "-" + str(today.tm_mon) + "-" + str(today.tm_mday) + "_" + str(today.tm_hour) + "h" + str(today.tm_min) + "m" + str(today.tm_sec)
    os.system("mkdir -p Logs/" + logsFolder)
    print("mkdir -p Logs/" + logsFolder)

    # Get the last version of the image.
    str2 = "sudo docker pull {} ".format(images[i % len(images)])
    print("Recuperation dernière version de l'image {}".format(images[i % len(images)]))
    os.system(str2)

    # Main command which run a docker which execute the tuxLogs.py script and write the logs in output.logs
    chaine = 'sudo docker run -it ' + images[i % len(images)] + ' /TuxML/tuxLogs.py | tee Logs/' + logsFolder + '/output.logs'
    print("\n=============== Docker n°{} ===============".format(i+1))
    print(chaine)
    print("==========================================\n")
    os.system(chaine)

    # Get the logs from the last used container.
    dockerid = os.popen("sudo docker ps -lq", "r")
    dock = dockerid.read()
    dock = dock[0:len(dock) -1]
    stdlogs = 'sudo docker cp {}:/TuxML/linux-4.13.3/logs/std.logs ./Logs/{}'.format(dock, logsFolder)
    errlogs = 'sudo docker cp {}:/TuxML/linux-4.13.3/logs/err.logs ./Logs/{}'.format(dock, logsFolder)
    print("Recovery of logs in the folder ./Logs/{}".format(logsFolder))
    os.system(tuxmllogs)
    os.system(stdlogs)
    os.system(errlogs)

    # Clean all the containers used before.
    if "--clean" in argv or "-c" in argv:
        print("Cleaning containers . . .")
        os.system("sudo docker rm -v $(docker ps -aq)")
        print("Clean done!")
    else:
        print("Option {} unknown.".format(argv[2]))
        exit()

    print("")

# The end
print("Your tamago... database ate {} compilation data, come back later to feed him again !".format(nb))
print("")
