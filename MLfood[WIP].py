import os;
from sys import argv


#Erreur si le nombre de compilation a lancer est vide
if len(argv) == 1:
    print("Veuillez préciser un nombre de compilation a lancer.")
    exit(1)

# On recupere le nombre de compilation a lancer
nb = int(argv[1])

# Doit contenir la liste des différentes URL d'images systemes contenant le/les scripts tuxml d'execution.
images = ["url1","url2","url3"]


# Pour chaque url dans la liste d'url on lance un nouveau docker qui lance la commande TuxML
for i in range(nb):
    str = 'docker run -i -t {} /bin/bash'.format(images[i % len(images)])
    print("\n"+str)
    os.system(str)
