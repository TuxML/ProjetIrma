#!/usr/bin/python3

import os

# Start of the script

print("Welcome, this is the TuxML Project Docker Image Manager")
# print("What do you want to do ?")

# print("B : Build une nouvelle image \n P : Build et Push une image existante")

print("Update of the docker image tuxml/tuxmldebian")

# Build the choosen docker image
str1 = 'sudo docker build -t tuxml/tuxmldebian .'
resb = os.system(str1)

if resb != 0:
    print("erreur {}".format(resb))

print("Push of the image on the distant repository")

# Push of the docker image on docker hub
str2 = 'sudo docker push tuxml/tuxmldebian'
os.system(str2)
