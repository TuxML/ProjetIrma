#!/usr/bin/python3

# call: python3 get_options_prompt.py 2>/dev/null to ignore warning messages
# you should put this script in the source folder of a kernel.
# You may also edit the inDIR (source path that contains the Kconfig files).

import sys
from kconfiglib import Kconfig, Symbol, Choice, MENU, COMMENT, KconfigError
import os, fnmatch
import csv


# the kernel location
inDIR = '.'
# the kconfig file pattern
pattern = 'Kconfig*'
# the list of gathered kconfig files
fileList = []
# the help dict: keys are config names, values are help messages (when exist)
helps = {}

# Gathering all the kconfig files of the kernel
for dName, sdName, fList in os.walk(inDIR):
    for fileName in fList:
        # If is a Kconfig file
        if fnmatch.fnmatch(fileName, pattern):
            fileList.append(os.path.join(dName, fileName))


def analyse_help(node):
    while node:
        if isinstance(node.item, Symbol) and str(node.help) != "None":
            helpMsg = str(node.help)
            helps[node.item.name] = helpMsg.replace("\n"," ")

#            if "size" in helpMsg or "reduce" in helpMsg:
#                print(helpMsg)

        if node.list:
            analyse_help(node.list)

        node = node.next

# Browing the kconf files to analyse them
for kfile in fileList:
    try:
        kconf = Kconfig(kfile)
        analyse_help(kconf.top_node)
    except KconfigError:
        print("==>>> KconfigError for file %s"%(kfile))

# Saving the dic as an CSV file
with open('helpMsgs.csv', 'w') as file:
    for key in helps.keys():
        file.write("%s;%s\n"%(key,helps[key]))



