#!/usr/bin/python3


import os
import subprocess
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("number", type=int, help="The number of comparisons to do (all by default)", nargs='?', default=-1)
args = parser.parse_args()

number = args.number

if number == -1 and os.path.exists("./compare/"):
    number = len([name for name in os.listdir('./compare/')])

print("Number of comparison:", number, flush=True)

for i in range(number):

    print("Number:",i , flush=True)
    subprocess.run('./bloat-o-meter compare/' + str(i) + '/incr-vmlinux compare/' + str(i) + '/basic-vmlinux > compare/' + str(i) + '/diff_size.txt', shell=True)

print("Size compared", flush=True)
