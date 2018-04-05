#!/usr/bin/python3

## @file MLfood.py
# @author LE MASLE Alexis
# @copyright Apache License 2.0
# @brief Run a given number of kernel compilation
#
# @details This file has been created to fill a database in order to perform a Machine Learning algorithm.
# You specify the number of compilations to do in a Docker container then you can specify an incremental parameter used in tuxml.py
#
# First we check the presence of --dev to run the project on the development docker image tuxml/tuxmldebian:dev or the "prod" one.
# After checking all potential parameters the loop begin a new Docker container until the number "nbcompil" given. The incremental parameter
# is used in tuxml.py and if you do not precise a number, it will be set at 0 by default.
#
# For example with 10 compilations as the first parameter and 3 as the incremental parameter, MLfood.py is going to run 10 new containers
# and each one will run 4 compilations, the first is the original compilation then 3 compilations using data from the previous compilation in the same container.

#   Copyright 2018 TuxML Team
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import os
import time
import argparse
from sys import argv

def mlfood():

    ## COLORS
    WHITE           = "\033[0m"                # Default color
    GRAY            = "\033[38;5;7m"           # Debug
    BLACK           = "\033[38;5;16m"
    RED             = "\033[38;5;1m"           # Errors messages
    LIGHT_RED       = "\033[38;5;9m"
    GREEN           = "\033[38;5;2m"           # Success messages
    LIGHT_GREEN     = "\033[38;5;10m"
    ORANGE          = "\033[38;5;3m"
    LIGHT_ORANGE    = "\033[38;5;11m"
    BLUE_1          = "\033[38;5;4m"
    LIGHT_BLUE_1    = "\033[38;5;12m"
    BLUE_2          = "\033[38;5;6m"
    LIGHT_BLUE_2    = "\033[38;5;14m"
    PURPLE          = "\033[38;5;5m"
    LIGHT_PURPLE    = "\033[38;5;13m"

    # Creation of help and arguments parser
    print(LIGHT_BLUE_1)
    parser = argparse.ArgumentParser()
    parser.add_argument("nbcompil", type=int, help="Run MLfood into the given number of containers.")
    parser.add_argument("incremental", type=int, help="Used in a case of incremental compilation with <Integer> compilation in a container.", nargs='?', default=0)
    parser.add_argument("--no-clean", help="Do not delete past containers.", action="store_true")
    parser.add_argument("--reset-logs", help="Delete all the saved logs and exit.", action="store_true")
    parser.add_argument("--dev", help="Use image in current development.", action="store_true")
    args = parser.parse_args()

    print(args.incremental)
    print(GRAY)

    # Must contain the list of differents systems images URLs with the execution tuxml script.
    images = []
    dev = ""
    if args.dev:
        images = ["tuxml/tuxmldebian:dev"]
        dev = "--dev"
    else:
        print(ORANGE)
        print("Without '--dev' the image is the functionnal version 'prod' of tuxmldebian:prod")
        print("With '--dev' it will use the current dev version tuxmldebian:dev")
        print(GRAY)

        yn = input("Are you sure you want to run MLfood without dev ? (y/n)")
        yn.lower()

        if yn == "y":
            images = ["tuxml/tuxmldebian:prod"]
        else:
            print(ORANGE + "Abort" + GRAY)
            exit(0)

    # Check if there is the --reset-logs option to erase all the logs.
    if args.reset_logs:
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
    if args.nbcompil >= 50:
        print(ORANGE + "Are-you sure you want to start " + str(args.nbcompil) + " compilation? (y/n)")
        print('Canceling it would take as much Ctrl+C as the remaining number of compilations.')
        ok = input()
        ok.lower()
        if ok != "y":
            print("Canceled")
            exit(0)

    print(GRAY)

    # Retrieves the number of compilation to run.
    if args.nbcompil <= 0:
        print(RED + "Please enter a non-zero positive integer." + GRAY)
        exit(0)

    # The image list must not be empty.
    if len(images) == 0:
        print("There are no images.")
        exit(0)

    # We check if the user is a super-user.
    if os.getuid() != 0:
        print(LIGHT_BLUE_1 + 'Docker needs super-user privileges to run' + GRAY)


    # For each url in the url list "images", we run a new docker which run the TuxML command nbcompil times and saves the logs.
    for i in range(args.nbcompil):
        print("")

        # Get the last version of the image.
        str2 = "sudo docker pull " + images[i % len(images)]
        print(LIGHT_PURPLE + "Recovering the last docker image " + images[i % len(images)] + "\n")
        os.system(str2)
        print(GRAY)

        # Generation of the logs folder create thanks to the execution date
        today = time.localtime(time.time())
        logsFolder = time.strftime("%Y%m%d_%H%M%S", time.gmtime(time.time()))
        if not os.path.exists("Logs/"+logsFolder):
            os.makedirs("Logs/" + logsFolder)

        # Main command which run a docker which execute the tuxLogs.py script and write the logs in output.logs
        chaine = 'sudo docker run -it ' + images[i % len(images)] + ' /TuxML/tuxLogs.py ' + str(args.incremental) + ' | tee Logs/' + logsFolder + '/output.log'
        print(LIGHT_BLUE_1 + "\n=============== Docker number " + str(i + 1)+ " ===============")
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
        dockerid.close()
        print(GRAY)

        # Clean all the containers used previously.
        if args.no_clean:
            print(LIGHT_PURPLE + "Cleaning containers . . .")
            os.system("sudo docker rm -v $(sudo docker ps -aq)")
            print("Clean done!")
            print("")

        print(LIGHT_BLUE_1 + "==========================================\n" + GRAY)


    # The end
    print(LIGHT_BLUE_1 + "Your tamago... database Irma_DB ate " + str(args.nbcompil) + " compilation data, come back later to feed it!" + GRAY)
    print("")


mlfood()
