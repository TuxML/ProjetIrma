#!/usr/bin/python3

import os

print("Mise a jour de l'image tuxmldebian")

str1 = 'sudo docker build -t tuxml/tuxmldebian .'

os.system(str1)

print("Push de l'image sur le repo")

str2 = 'sudo docker push tuxml/tuxmldebian'

os.system(str2)
