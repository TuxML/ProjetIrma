#!/usr/bin/python3

import os
from sys import argv

# We define the function use in the script
def dockerBuild():
    print("Update of the docker image tuxml/tuxmldebian")
    # Build the choosen docker image
    str1 = 'sudo docker build -t tuxml/tuxmldebian .'
    os.system(str1)

def dockerPush():
    print("Push of the image on the distant repository")
    # Push of the docker image on docker hub
    strpush = 'sudo docker push tuxml/tuxmldebian'
    rstrpush = os.system(strpush)
    # If needed, login to the repository
    if rstrpush == 256:
        str3 = 'sudo docker login'
        os.system(str3)

# Start of the script

# Refactor needed with the use of argparse
# We check if the script have an option to it, if not we run the program with GUI (not yet implement)
if len(argv) == 1:
    print("The graphical mode of TPDIM is not implemented yet.")
    exit(0)

# Show the options if the user ask for it
if "-h" in argv or "--help" in argv:
    print("")
    print("Options : -b [.|directory path], --build     Build an image with the folder give in option, the folder must have a valid DockerFile")
    print("          -g <parent image> [dependances text file], --generate <parent_image> [dependances text file]    Generate a DockerFile, suit for TuxML, with the parent image and add the optional dependances.")
    exit(0)

# We check if the user is a super-user.
if os.getuid() != 0:
    print('Docker needs to be launch with super user rights')
    exit(1)
