#!/usr/bin/env python3

import argparse
import sys
import subprocess


def rewrite(option, mode, path):

    try:
        assert mode in ("y", "n", "m"), "Error: In \'" + \
                        rewrite.__name__ + "\' function, mode must be 'y', 'n' or 'm'"
    except AssertionError as ae:
        print(ae, file=sys.stderr)
        exit(0)

    been = ""
    if mode == "y":
        been = " activated"
    elif mode == "n":
        been = " disactivated"
    elif mode == "m":
        been = " set at \"module\""

    lines = ""
    with open(path, "r") as f:
        lines = f.readlines()

        active = "CONFIG_" + option + "=y\n"
        mod = "CONFIG_" + option + "=m\n"
        inactive = "# CONFIG_" + option + " is not set\n"

        exist = False
        for line in lines:

            if line == active:
                if mode == "n":
                    lines[lines.index(line)] = inactive
                    break
                elif mode == "m":
                    lines[lines.index(line)] = mod
                    break
                else:
                    been = " is already activated"
                    break
                exist = True

            elif line == mod:
                if mode == "y":
                    lines[lines.index(line)] = active
                    break
                elif mode == "n":
                    lines[lines.index(line)] = inactive
                else:
                    been = " is already \"module\""
                    break
                exist = True

            elif line == inactive:
                if mode == "y":
                    lines[lines.index(line)] = active
                    break
                elif mode == "m":
                    lines[lines.index(line)] = mod
                    break
                else:
                    been = " is already disactivated"
                    break
                exist = True

    if not exist:
        print("CONFIG_" + option + " has not been found in " + path)
        return -1

    else:
        with open(path, "w") as f:
            f.writelines(lines)

        print(option + been)
    return 0


def independant_rewrite(args):
    import random

    independant = ["XFS_FS", "SND_DICE", "SND_ISIGHT", "SPEAKUP_SYNTH_DECEXT", "CRC32", "TCP_CONG_ILLINOIS",
                   "BCM2835_VCHIQ", "TOUCHSCREEN_HAMPSHIRE", "COMEDI_DT2817", "MII", "BT_INTEL", "VETH"]
    random.shuffle(independant)

    if args.randomize_number > len(independant):
        args.randomize_number = len(independant)
    elif args.randomize_number < 0:
        args.randomize_number = 0

    mode = ["y","n","m"]
    for i in range(args.randomize_number):
        random.shuffle(mode)
        rewrite(independant[i], mode[0], args.path)

    if args.verbose:
        subprocess.run("cat " + args.path, shell=True)


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v", "--verbose", help="Print the .config file after the work is done and succeed", action="store_true")
    parser.add_argument(
        "--path", type=str, help="Path to the .config file", default=".config")

    subparsers = parser.add_subparsers(
        help="Change a tristate option value", dest="command")

    parser1 = subparsers.add_parser(
        "option", help="Change the value of a given option with given value in 'y','n' or 'm'")
    parser1.add_argument("option_config", type=str,
                         help="The configuration option to change")
    parser1.add_argument(
        "mode", type=str, help="The mode to set to the configuration option", choices=['y', 'n', 'm'])

    parser2 = subparsers.add_parser(
        "random", help="Change a given number of tristate with random values")
    parser2.add_argument("randomize_number", type=int,
                         help="The number of tristate to change with random value in 'y,'n' or 'm'")

    args = parser.parse_args()

    # print(" | ".join([k + ' : ' + str(vars(args)[k])
    #                   for k in vars(args)]), flush=True)

    if args.command is None:
        parser.print_help()

    if args.command == "random":
        independant_rewrite(args)


if __name__ == "__main__":
    main()


#
