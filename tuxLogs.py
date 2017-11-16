#!/usr/bin/python3

import os

# The command which we print and we write the output in the tuxML.logs
chaine = '/TuxML/core/tuxml.py /TuxML/linux-4.13.3 --debug | tee /TuxML/linux-4.13.3/logs/tuxML.logs'
os.system(chaine)
