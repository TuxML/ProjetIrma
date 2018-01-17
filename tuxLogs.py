#!/usr/bin/python3

import os

# # Update the
# print('Retrieves latest version of TuxML scritps...')
# os.system('cd /TuxML/')
# os.system('git pull')
# os.system('git checkout dev')

# The command which we print and we write the output in the tuxML.logs
print('Starting tuxml.py ...')
os.system('/TuxML/core/tuxml.py /TuxML/linux-4.13.3 -v 1')
