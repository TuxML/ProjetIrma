import os;


# Doit contenir la liste des différentes URL d'images systemes contenant le/les scripts tuxml d'execution.
lurl = ["url1","url2","url3"]


for url in lurl :
    str = 'docker run -i -t {} /bin/bash'.format(url);
    system(str);
