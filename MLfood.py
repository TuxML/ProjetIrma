import os
import sys


# Error if there is no argument "number" of compilation to run.
if len(sys.argv) == 1:
    print("Veuillez préciser un nombre de compilation a lancer.")
    exit(1)

# Retrieves the number of compilation to run.
nb = int(sys.argv[1])

# Must contain the list of differents systems images URLs with the execution tuxml script.
images = ["tuxmfood"]

# The image list must not be empty.
if len(images) == 0:
	print("Il n'a aucune images système\n")
	exit(1)

# For each url in the url list "images", we run a new docker which run the TuxML command.
for i in range(nb):
	print("\n=============== Docker n°{} ===============".format(i+1))
	str = 'sudo docker run -t {} /bin/ls'.format(images[i % len(images)])
	print(str)
	print("=========================================\n")
	os.system(str)
