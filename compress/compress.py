#!/usr/bin/python3

import subprocess
import re
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("compression", type=str, choices= ["GZIP","BZIP2","LZMA","XZ","LZO","LZ4"], help="Precise the compression you wish to use in the .config file")
args = parser.parse_args()

def rewrite(old, new):
    f = open(".config", "r")
    lines = f.readlines()
    f.close()

    for line in lines:
        if line == old + "\n":
            lines[lines.index(line)] = new + '\n'

            f = open(".config", "w")
            f.seek(0)
            f.writelines(lines)
            f.close()
            print("REWRITING DONE")
            return 0

    return -1

# enable a compression and disable the others
def enable(compress):

    compression = ["GZIP","BZIP2","LZMA","XZ","LZO","LZ4"]
    if compress not in compression:
        print(compress,"not in compression list")
        return -1

    # enable
    rewrite("# CONFIG_KERNEL_" + compress+ " is not set", "CONFIG_KERNEL_" + compress + "=y")

    # disable
    for c in compression:
            if not c == compress:
                rewrite("CONFIG_KERNEL_" + c + "=y", "# CONFIG_KERNEL_" + c + " is not set")

    return 0

enable(args.compression)

print("")
subprocess.run("cat .config | grep CONFIG_KERNEL", shell=True)
