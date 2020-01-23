#!/usr/bin/python3

import sys
from kconfiglib import Kconfig, Symbol


def get_details(node,option_name):
    while node:
        if isinstance(node.item, Symbol):
            if option_name in str(node):
                print(str(node))
                exit(0)

        if node.list:
            get_details(node.list,option_name)

        node = node.next


# start
kconf = Kconfig(sys.argv[1])
suffix = "config "
option_test = "DMI"
option_name = suffix + option_test
get_details(kconf.top_node,option_name)






