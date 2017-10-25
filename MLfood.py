import os
from sys import argv


# Error if there is no argument "number" of compilation to run.
if len(argv) == 1:
    print("Please specify a number of compilation to launch.")
    exit()

# Retrieves the number of compilation to run.
nb = int(argv[1])

if nb <= 0:
    print("Please enter a non-zero positive integer.")
    exit()

# Must contain the list of differents systems images URLs with the execution tuxml script.
images = ["tuxml/tuxmldebian"]

# The image list must not be empty.
if len(images) == 0:
	print("There is no images.")
	exit()

# For each url in the url list "images", we run a new docker which run the TuxML command.
for i in range(nb):
	print("\n=============== Docker n°{} ===============".format(i+1))
	str = 'sudo docker run -t -i {} /TuxML/tuxml.py /TuxML/linux-4.13.3'.format(images[i % len(images)])
	print(str)
	print("=========================================\n")
	os.system(str)
