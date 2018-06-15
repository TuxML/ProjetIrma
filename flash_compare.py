#!/usr/bin/env python3


import os
import subprocess
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("number", type=int, help="The number of comparisons to do (all by default)", nargs='?', default=-1)
args = parser.parse_args()

def diff_size(n):

    number = n

    if not os.path.exists("./compare/"):
        os.makedirs("./compare/")

    max_number = len([name for name in os.listdir('./compare/')])

    if number > max_number:
        number = max_number
    elif number < 0:
        number = 0

    print("Number of comparisons:", number, flush=True)

    for i in range(number):

        print("Number:",i , flush=True)
        subprocess.run('./bloat-o-meter compare/' + str(i) + '/incr-vmlinux compare/' + str(i) + '/basic-vmlinux > compare/' + str(i) + '/diff_size.txt', shell=True)

    print("Size compared", flush=True)

if __name__ == "__main__":
    diff_size(args.number)
