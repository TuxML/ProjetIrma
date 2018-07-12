#!/usr/bin/env python3

import argparse
import sys
import subprocess

"""
    Liste d'options indépendantes:
        - KASAN_OUTLINE (bool)
        - MODULES (bool)
        - GENERIC_ALLOCATOR (bool)
        - XFS_FS (tristate)

"""


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


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("option_config", type=str,
                        help="The configuration option to change")
    parser.add_argument(
        "mode", type=str, help="The mode to set to the configuration option", choices=['y', 'n', 'm'])
    parser.add_argument(
        "-v", "--verbose", help="Print the .config file after the work is done and succeed", action="store_true")
    parser.add_argument(
        "--path", type=str, help="Path to the .config file", default=".config")
    args = parser.parse_args()

    rc = rewrite(args.option_config, args.mode, args.path)

    if args.verbose and rc == 0:
        subprocess.run("cat " + args.path, shell=True)


if __name__ == "__main__":
    main()
