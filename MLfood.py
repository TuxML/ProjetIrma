import os
import sys


# Error if there is no argument "number" of compilation to run.
if len(sys.argv) == 1:
    print("Veuillez préciser un nombre de compilation a lancer.")
    exit(1)
    
# Retrieves the number of compilation to run.
nb = int(sys.argv[1])

# Must contain the list of differents systems images URLs with the execution tuxml script.
images = ["url1","url2","url3"]

# The image list must not be empty.
if len(images) == 0:
	print("Il n'a aucune images système\n")
	exit(1)

# For each url in the url list "images", we run a new docker which run the TuxML command.
for i in range(nb):
    str = 'sudo docker run -i -t {} /bin/bash'.format(images[i % len(images)])
    print("\n"+str)
    os.system(str)
