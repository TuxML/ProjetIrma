#!/usr/bin/env python3


import os
import subprocess
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("number", type=int, help="The number of comparisons to do (all by default)", nargs='?', default=-1)
args = parser.parse_args()

if not os.path.exists("./compare/"):
    os.makedirs("./compare/")

max_number = len([name for name in os.listdir('./compare/')])

def diff_size(n):

    number = n

    if number > max_number:
        number = max_number
    elif number < 0:
        number = max_number

    print("Number of comparisons:", number, flush=True)

    diff = {}

    for i in range(number):

        print("Number:",i , flush=True, end='')
        subprocess.run('./bloat-o-meter compare/' + str(i) + '/incr-vmlinux compare/' + str(i) + '/basic-vmlinux > compare/' + str(i) + '/diff_size.txt', shell=True, stdout=open("compare/" + str(i) + "/diff_size.txt",'w'))

        with open("compare/" + str(i) + "/diff_size.txt", "r") as f:
            lines = f.readlines()
            tmp = lines[-1].split()[-1]
            diff[str(i)] = tmp
            print(" " + tmp, flush=True)

    print("Percentage of differences between incremental and basic compiled kernels:")
    liste = list(diff.values())
    print(liste)

    temp = 0.0
    for i in range(len(liste)):
        temp += float(liste[i][1:-1])

    average = '+' + str(temp/len(liste))[:6] + '%'
    print("average difference:", average, flush=True)

if __name__ == "__main__":
    diff_size(args.number)
