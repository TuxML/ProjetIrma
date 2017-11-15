#!/usr/bin/python3

import os

# Start of the script

print("Welcome, this is the TuxML Project Docker image manager")
print("What do you want to do ?")

print("Update of the docker image tuxml/tuxmldebian")

# Build the choosen docker image
str1 = 'sudo docker build -t tuxml/tuxmldebian .'
os.system(str1)

print("Push of the image on the distant repository")

# Push of the docker image on docker hub
str2 = 'sudo docker push tuxml/tuxmldebian'
os.system(str2)
