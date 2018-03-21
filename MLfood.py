#!/usr/bin/python3

import os
import time

from sys import argv

# Author Alexis LE MASLE


## COLORS
WHITE           = "\033[0m"                # Default color
GRAY            = "\033[38;5;7m"           # Debug
BLACK           = "\033[38;5;16m"
RED             = "\033[38;5;1m"           # Errors messages
LIGHT_RED       = "\033[38;5;9m"
GREEN           = "\033[38;5;2m"           # Success messages
LIGHT_GREEN     = "\033[38;5;10m"
ORANGE          = "\033[38;5;3m"           #
LIGHT_ORANGE    = "\033[38;5;11m"
BLUE_1          = "\033[38;5;4m"
LIGHT_BLUE_1    = "\033[38;5;12m"
BLUE_2          = "\033[38;5;6m"
LIGHT_BLUE_2    = "\033[38;5;14m"
PURPLE          = "\033[38;5;5m"
LIGHT_PURPLE    = "\033[38;5;13m"




# Error if there is no argument "number" of compilation to run.
if len(argv) == 1 or "-h" in argv or "--help" in argv:
    print(LIGHT_BLUE_1 + "")
    print("Try: ./MLfood.py <Integer> [<Integer>] [Options]")
    print("")
    print("The first Integer run MLfood into the given number of containers")
    print("The second Integer is optional, it is used in a case of incremental compiling with <Integer> compiling in a container")
    print("The default number of compiling in a container is set as 1")
    print("")
    print("Options: --no-clean    Do not delete past containers")
    print("         -h, --help    Prompt Options")
    print("         --reset-logs  Delete all the saved logs")
    print("         --dev         Use images in current developpement")
    print("" + GRAY)
    exit(0)

# Check if there is the --reset-logs option to erase all the logs.
if "--reset-logs" in argv:
    print(ORANGE + "Are-you sure you want to delete all the saved logs? (y/n)")
    reset = input()
    reset.lower()
    if reset == "y":
        print("Deleting all the logs in Logs/...")
        os.system("rm -rf Logs/*")
        print("Delete done.")
        print("" + GRAY)
        exit(0)
    else:
        print("")
        print("Logs are not deleted.")
        print("" + GRAY)
        exit(0)

# Convert the parameter in an Integer which is the number of compilation to do.
# If the number is above 50, the scrypt will ask for a confirmation
try:
    nb = int(argv[1])
    if nb >= 50:
        print(ORANGE + "Are-you sure you want to start " + str(nb) + " compilation? (y/n)")
        print('Canceling it would take as much Ctrl+C as the remaining number of compiling.')
        ok = input()
        ok.lower()
        if ok != "y":
            print("Canceled")
            exit(0)
except Exception as e:
    print(ORANGE)
    print("Please specify a valid number of compilation to launch.")
    print("Command ./MLfood.py <Integer> [Option]")
    print(GRAY)
    exit(0)

print(GRAY)

# Retrieves the number of compilation to run.
if nb <= 0:
    print(RED + "Please enter a non-zero positive integer." + GRAY)
    exit(0)

# Must contain the list of differents systems images URLs with the execution tuxml script.
images = []
dev = ""
if "--dev" in argv:
    images = ["tuxml/tuxmldebian:dev"]
    dev = "--dev"
else:
    images = ["tuxml/tuxmldebian:prod"]

incrN = 0

if len(argv) == 3:
    try:
        incrN = int(argv[2])
    except Exception as e:
        pass


# The image list must not be empty.
if len(images) == 0:
    print("There is no images.")
    exit(0)

# We check if the user is a super-user.
# Restarting with sudo.
if os.getuid() != 0:
    print(LIGHT_BLUE_1 + 'Docker needs to start with sudo mode' + GRAY)


# For each url in the url list "images", we run a new docker which run the TuxML command nb times and saves the logs.
for i in range(nb):
    print("")

    # Get the last version of the image.
    str2 = "sudo docker pull " + images[i % len(images)]
    print(ORANGE + "Recovering the last docker image " + images[i % len(images)])
    os.system(str2)
    print(GRAY)

    # Generation of the logs folder create thanks to the execution date
    today = time.localtime(time.time())
    logsFolder = time.strftime("%Y%m%d_%H%M%S", time.gmtime(time.time()))
    if not os.path.exists("Logs/"+logsFolder):
        os.makedirs("Logs/" + logsFolder)

    # Main command which run a docker which execute the tuxLogs.py script and write the logs in output.logs
    chaine = 'sudo docker run -i ' + images[i % len(images)] + ' /TuxML/tuxLogs.py ' + str(incrN) + " " + dev + ' | tee Logs/' + logsFolder + '/output.log'
    print(LIGHT_BLUE_1 + "\n=============== Docker number " + str(i + 1)+ " ===============")
    # print(chaine)
    print("")
    os.system(chaine)

    # Get the logs std.logs and err.logs from the last used container and retrieves the ".config" file.
    dockerid = os.popen("sudo docker ps -lq", "r")
    dock = dockerid.read()
    dock = dock[0:len(dock) -1]
    stdlogs = 'sudo docker cp ' + dock + ':/TuxML/linux-4.13.3/logs/std.log ./Logs/' + logsFolder
    errlogs = 'sudo docker cp ' + dock + ':/TuxML/linux-4.13.3/logs/err.log ./Logs/' + logsFolder
    configFile = 'sudo docker cp ' + dock + ':/TuxML/linux-4.13.3/.config ./Logs/' + logsFolder + '/' + logsFolder + '.config'
    print("")
    print(LIGHT_PURPLE + "Fetch logs and .config file to the folder ./Logs/" + logsFolder )
    os.system(stdlogs)
    os.system(errlogs)
    os.system(configFile)
    print(GRAY)

    # Clean all the containers used previously.
    if "--no-clean" not in argv:
        print(LIGHT_PURPLE + "Cleaning containers . . .")
        os.system("sudo docker rm -v $(sudo docker ps -aq)")
        print("Clean done!")
        print("")
    elif argv[2] != None:
        print(RED + "Option " + argv[2] + " unknown." + GRAY)
        print("")
        exit(0)

    print(LIGHT_BLUE_1 + "==========================================\n" + GRAY)

# The end
print(LIGHT_BLUE_1 + "Your tamago... database ate " + str(nb) + " compilation data, come back later to feed it!" + GRAY)
print("")
