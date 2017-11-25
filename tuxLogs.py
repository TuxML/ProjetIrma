#!/usr/bin/python3

import os

# The command which we print and we write the output in the tuxML.logs

print(':Updating:')
os.system('apt update')

print('Starting tuxml.py ...')
os.system('/TuxML/core/tuxml.py /TuxML/linux-4.13.3 -v')
