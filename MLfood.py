import os
import sys


# Error if there is no argument "number" of compilation to run.
if len(sys.argv) == 1:
    print("Please specify a number of compilation to launch.")
    exit()

# Retrieves the number of compilation to run.
nb = int(sys.argv[1])

if nb <= 0:
    print("Please enter a non-zero positive integer.")
    exit()

# Must contain the list of differents systems images URLs with the execution tuxml script.
images = ["debian","archlinux/base","url3"]

# The image list must not be empty.
if len(images) == 0:
	print("There is no images.")
	exit()

# For each url in the url list "images", we run a new docker which run the TuxML command.
for i in range(nb):
	print("\n=============== Docker n°{} ===============".format(i+1))
	str = 'sudo docker run -t {} /bin/ls'.format(images[i % len(images)])
	print(str)
	print("=========================================\n")
	os.system(str)
