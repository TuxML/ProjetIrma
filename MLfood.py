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

# We check if the user is a super-user.
# Restarting with sudo.
if os.getuid() != 0:
    print('Docker needs to start with sudo mode')

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
        print('Canceling it would take as much Ctrl+C as the remaining number of compiling.')
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

    # Get the last version of the image.
    str2 = "sudo docker pull " + images[i % len(images)]
    print("Recovering the last docker image " + images[i % len(images)])
    os.system(str2)

    # Generation of the logs folder create thanks to the execution date
    today = time.localtime(time.time())
    logsFolder = time.strftime("%Y%m%d_%H%M%S", time.gmtime(time.time()))
    if not os.path.exists("Logs/"+logsFolder):
        os.makedirs("Logs/" + logsFolder)

    # Main command which run a docker which execute the tuxLogs.py script and write the logs in output.logs
    chaine = 'sudo docker run -it ' + images[i % len(images)] + ' /TuxML/tuxLogs.py | tee Logs/' + logsFolder + '/output.log'
    print("\n=============== Docker n°" + str(i + 1)+ " ===============")
    print(chaine)
    print("==========================================\n")
    os.system(chaine)

    # Get the logs std.logs and err.logs from the last used container and retrieves the ".config" file.
    dockerid = os.popen("sudo docker ps -lq", "r")
    dock = dockerid.read()
    dock = dock[0:len(dock) -1]
    stdlogs = 'sudo docker cp ' + dock + ':/TuxML/linux-4.13.3/logs/std.log ./Logs/' + logsFolder
    errlogs = 'sudo docker cp ' + dock + ':/TuxML/linux-4.13.3/logs/err.log ./Logs/' + logsFolder
    configFile = 'sudo docker cp ' + dock + ':/TuxML/linux-4.13.3/.config ./Logs/' + logsFolder + '/' + logsFolder + '.config'
    print("Fetch logs and .config file to the folder ./Logs/" + logsFolder)
    os.system(stdlogs)
    os.system(errlogs)
    os.system(configFile)

    # Clean all the containers used previously.
    if not "--no-clean" in argv:
        print("Cleaning containers . . .")
        os.system("sudo docker rm -v $(sudo docker ps -aq)")
        print("Clean done!")
    else:
        print("Option " + argv[2] + " unknown.")
        exit(0)

    print("")

# The end
print("Your tamago... database ate " + str(nb) + " compilation data, come back later to feed it!")
print("")
