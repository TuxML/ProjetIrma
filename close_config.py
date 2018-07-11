#!/usr/bin/env python3

from sys import argv
import argparse
import kconfiglib


def main():

    # parser = argparse.ArgumentParser()
    # parser.add_argument(
    #     "-y", "--yes", help="Number of options you want to set on 'y' (yes)")
    # parser.add_argument(
    #     "-n", "--no", help="Number of options you want to set on 'n' (no)")
    # parser.add_argument(
    #     "-m", "--modules", help="Number of options you want to set on 'm' (module)")
    # parser.add_argument(
    #     "--path", help="Only edit an existing .config (create a new one by default)", nargs='?', default='.config')
    # args = parser.parse_args()

    if len(argv) == 1:
        # parser.print_help()
        exit(0)

    # print(" | ".join([k + ' : ' + str(vars(args)[k])
    #                   for k in vars(args)]), flush=True)

    # config_file = args.path

    k = kconfiglib.Kconfig()

    # k.load_config(args.path)
    k.load_config(".config")
    # data_fill = []
    tmp = k.defined_syms
    
    print("")
    for i in range(10):
        sym = tmp[i]
        print(sym.name, ":", kconfiglib.TYPE_TO_STR[sym.orig_type].upper(), flush=True)

    print("")
    

    # print(data_fill)


if __name__ == "__main__":
    main()
