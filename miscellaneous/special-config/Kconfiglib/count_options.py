#!/usr/bin/python3

import sys
from kconfiglib import Kconfig, Symbol
from kernel_options_csv import CSV_FILE_PATH

COUNT = 0


def count_items(node):
    while node:
        global COUNT
        if isinstance(node.item, Symbol):
            COUNT += 1

        if node.list:
            count_items(node.list)

        node = node.next


# start
kconf = Kconfig(sys.argv[1])
count_items(kconf.top_node)
fichier = open(CSV_FILE_PATH, "a") # here we open an already opened file, TODO: check whether its dangerous or not
fichier.write("{}\n".format(COUNT))
fichier.close()





