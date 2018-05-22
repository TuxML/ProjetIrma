#!/usr/bin/python3

## @file MLfood.py
# @author LE MASLE Alexis
# @copyright Apache License 2.0
# @brief Run a given number of kernel compilation
#
# @details This file has been created to fill a database in order to perform a Machine Learning algorithm.
# You specify the number of compilations to do in a Docker container then you can specify an incremental parameter used in tuxml.py
#
# First we check the presence of --dev parameter to run the project on the development docker image tuxml/tuxmldebian:dev or the "prod" one.
# After checking all potential parameters the loop begin a new Docker container until the number "nbcompil" given has been reached. The incremental parameter
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
import subprocess
import time
import argparse


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
LIGHT_BLUE_1    = "\033[38;5;12m"          # Informations
BLUE_2          = "\033[38;5;6m"
LIGHT_BLUE_2    = "\033[38;5;14m"
PURPLE          = "\033[38;5;5m"
LIGHT_PURPLE    = "\033[38;5;13m"          # Informations



#################### Section 1 ####################
# Creation of help and arguments parser
print(LIGHT_BLUE_1)
parser = argparse.ArgumentParser()
parser.add_argument("nbcompil", type=int, help="Run MLfood into the given number of containers.")
parser.add_argument("incremental", type=int, help="Used in a case of incremental compilation with <Integer> compilation in a container.", nargs='?', default=0)
parser.add_argument("--no-clean", help="Do not delete past containers.", action="store_true")
parser.add_argument("--reset-logs", help="Delete all the saved logs and exit.", action="store_true")
parser.add_argument("--dev", help="Use image in current development.", action="store_true")
parser.add_argument("--force-compilation-limits", help="Use this option to pass the user check if the requested number of compilations exceeds 50.", action="store_true")
parser.add_argument("--no-check-log", help="Do not compute the Logs folder size at the end of compilation.", action="store_true")
args = parser.parse_args()
print(GRAY)

## The main function, used to be a script but encapsulated in a function
# in order to hide local variables and make the doc more readable.
#
# All sections annoted in the code are explained in the documentation
def mlfood():

    #################### Section 2 ####################
    # Check if there is the --reset-logs option to erase all the logs.
    if args.reset_logs:
        print(ORANGE + "Are-you sure you want to delete all the saved logs? (y/n)")
        reset = input()

        while reset != 'n' and reset != 'y':
            reset = input("Please choose between 'y' and 'n'")

        reset.lower()
        if reset == "y":
            print("Deleting all the logs in Logs/...")
            subprocess.run("rm -rf Logs/*", shell=True).stdout
            print("Delete done.")
            print("" + GRAY)
            exit(0)
        elif reset == 'n':
            print("")
            print("Logs are not deleted.")
            print(GRAY)
            exit(0)

    #################### Section 3 ####################
    images = []
    dev = ""
    if args.dev:
        images = ["tuxml/tuxmldebian:dev"]
        dev = "--dev"
    else:
        print(ORANGE)
        print("Without '--dev' the image is the functionnal version 'prod' of tuxmldebian:prod (stable)")
        print("With '--dev' it will use the current dev version tuxmldebian:dev (possibly unstable)")

        ok = input("Are you sure you want to run MLfood without dev ? (y/n)")

        while ok != 'n' and ok != 'y':
            ok = input("Please choose between 'y' and 'n'")

        ok.lower()
        print(GRAY)

        if ok == "y":
            images = ["tuxml/tuxmldebian:prod"]
        elif ok == 'n':
            print(ORANGE + "Abort" + GRAY)
            exit(0)

    #################### Section 4 ####################
    # Convert the parameter in an Integer which is the number of compilation to do.
    # If the number is above 50 and the option "-y" is not enable, the script will ask for a confirmation
    if args.nbcompil >= 50 and not args.force_compilation_limits:
        print(ORANGE + "Are-you sure you want to start " + str(args.nbcompil) + " compilation?")
        print('Canceling it would take as much Ctrl+C as the remaining number of compilations.')
        ok = input("(y/n)")

        while ok != 'n' and ok != 'y':
            ok = input("Please choose between 'y' and 'n'")

        ok.lower()
        if ok == "n":
            print("Canceled")
            exit(0)

        elif ok == 'y':
            print(LIGHT_BLUE_1 + "Take a coffee and admire your " + str(args.nbcompil) + " compilations!" + GRAY)

    print(GRAY)

    #################### Section 5 ####################
    # Retrieves the number of compilation to run.
    if args.nbcompil <= 0:
        print(RED + "Please enter a non-zero positive integer." + GRAY)
        exit(0)

    # The image list must not be empty.
    if len(images) == 0:
        print("There are no images.")
        exit(0)

    # We check if the user is a super-user, to prevent users that the super-user privileges are used only to run dockers commands
    if os.geteuid() != 0:
        if args.nbcompil >= 5:
            print(LIGHT_BLUE_1 + "You should run MLfood.py with 'sudo' to run a big number of compilations.")
            print("If you do not,you will be asked to enter your password before and after each compilations." + GRAY)
        print(LIGHT_BLUE_1 + 'Docker needs super-user privileges to run' + GRAY)

    #################### Section 6 ####################
    # For each url in the url list "images", we run a new docker which run the TuxML command nbcompil times and saves the logs.
    for i in range(args.nbcompil):
        print("")

        #################### Section 7 ####################
        # Get the last version of the image.
        str2 = "sudo docker pull " + images[i % len(images)]
        print(LIGHT_PURPLE + "Recovering the last docker image " + images[i % len(images)] + "\n")
        subprocess.run(str2, shell=True).stdout
        print(GRAY)

        #################### Section 8 ####################
        # Generation of the logs folder create thanks to the execution date
        # today = time.localtime(time.time())
        logsFolder = time.strftime("%Y%m%d_%H%M%S", time.gmtime(time.time()))
        if not os.path.exists("Logs/"+logsFolder):
            os.makedirs("Logs/" + logsFolder)

        #################### Section 9 ####################
        # Main command which run a docker which execute the runandlog.py script and write the logs in output.logs
        chaine = 'sudo docker run -t ' + images[i % len(images)] + ' /TuxML/runandlog.py ' + str(args.incremental)
        print(LIGHT_BLUE_1 + "\n=============== Docker number " + str(i + 1)+ " ===============")
        print(GRAY)
        subprocess.run(chaine, shell=True).stdout

        #################### Section 10 ####################
        # Get the logs output.log, std.logs and err.logs from the last used container and retrieves the ".config" file.
        dockerid = os.popen("sudo docker ps -lq", "r")
        dock = dockerid.read()
        dock = dock[0:len(dock) -1]
        outputlog = 'sudo docker cp ' + dock + ':/TuxML/output.log ./Logs/' + logsFolder
        stdlogs = 'sudo docker cp ' + dock + ':/TuxML/linux-4.13.3/logs/std.log ./Logs/' + logsFolder
        errlogs = 'sudo docker cp ' + dock + ':/TuxML/linux-4.13.3/logs/err.log ./Logs/' + logsFolder
        configFile = 'sudo docker cp ' + dock + ':/TuxML/linux-4.13.3/.config ./Logs/' + logsFolder + '/' + logsFolder + '.config'
        print("")
        print(LIGHT_PURPLE + "Fetch logs and .config file from container:" + dock + " to the folder ./Logs/" + logsFolder )
        # Thoses following lines can print errors in the case where the compilation process has crash or even the Docker container.
        # Thoses errors are only due to the logs files that does not exist because of the process error.
        # Consider it as warnings.
        subprocess.run(outputlog, shell=True).stdout
        subprocess.run(stdlogs, shell=True).stdout
        subprocess.run(errlogs, shell=True).stdout
        subprocess.run(configFile, shell=True).stdout
        dockerid.close()
        print(GRAY)

        #################### Section 11 ####################
        # Clean all the containers used previously. Only if "--no-clean" is not given in argument.
        if not args.no_clean:
            print(LIGHT_PURPLE + "Cleaning containers . . .")
            subprocess.run("sudo docker rm -v $(sudo docker ps -aq)", shell=True).stdout
            print("Clean done!")
            print("")

        print(LIGHT_BLUE_1 + "==========================================\n" + GRAY)

    #################### Section 12 ####################
    # The end
    print(LIGHT_BLUE_1 + "Your tamago... database Irma_DB ate " + str(args.nbcompil * (args.incremental + 1)) + " compilations data, come back later to feed it!" + GRAY)
    print(LIGHT_PURPLE)
    print("Total number of containers used: " + str(args.nbcompil))
    print("Number of compilations in a container: " + str(args.incremental + 1) + " ( 1 basic compilation + " + str(args.incremental) + " incremental compilations )")
    print("Total number of compilations: " + str(args.nbcompil * (args.incremental + 1)) )
    print(GRAY)



# Check the size of log directory to remind the user to delete them.
def check_log():
    current_path = './Logs'
    list = os.listdir(current_path)
    raw_size = ''
    size = 0
    if len(list) > 0:

        for folder in list:
            path = current_path + '/' + folder

            if os.path.isdir(path):
                l = os.listdir(path)
                if len(l) > 0:
                    # Retrieves only files
                    files = [f for f in l if os.path.isfile(os.path.join(path, f))]
                    for file in files:
                        cmd = "wc -c " + path + "/" + file
                        raw_size = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
                        tmp = raw_size.stdout.read().decode()
                        tmp.replace("\n", " ")
                        size = size + int(tmp.split()[-2])
            # Case were there are files in the Logs/ level.
            else:
                raw_size = subprocess.Popen("wc -c " + path, shell=True,stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
                tmp = raw_size.stdout.read().decode()
                tmp.replace("\n", " ")
                size = size + int(tmp.split()[-2])

    # Alert if the logs exceeds 1 Mo
    # 1048576 one mebioctet
    # 1000000 one megaoctet
    # size = float(size/1048576.0)  # Mebioctet version
    size = float(size/1000000.0)    # Megaoctet version

    if size >= 10.0:
        print("You have " + RED + str(size)[0:4] + GRAY + " Mo of logs files, you should delete your logs.")
    elif size >= 1.0 and size < 10.0:
        print("You have " + ORANGE + str(size)[0:4] + GRAY + " Mo of logs files, do not forget to delete it to gain space.")
    elif size < 1.0:
        print("You have " + GREEN + str(size)[0:4] + GRAY + " Mo of logs files.")
    # print("You have " + ORANGE + str(size) + GRAY + " Bytes of logs files, do not forget to delete it to gain space." if size > 1048576 else '')



#################### Section 13 ####################
mlfood()
if not args.no_check_log:
    print("Checking local logs size ...")
    check_log()
