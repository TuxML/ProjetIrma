#!/usr/bin/env python3

import MySQLdb
import os
import subprocess
import argparse
import re
import core.tuxml_settings as tset

if not os.path.exists("./compare/"):
    os.makedirs("./compare/")

max_number = len([name for name in os.listdir('./compare/')])

def diff_time(n):

    number = n

    if number > max_number:
        number = max_number
    elif number < 0:
        number = max_number

    cid = {}

    for id in range(number):
        tmp_base = ""
        tmp_incr = ""
        with open('compare/'+ str(id) +'/incr-output.log') as file:
            for line in file:
                match = re.search('DATABASE CONFIGURATION ID=(\d+)', line)
                match2 = re.search('INCREMENTAL CONFIGURATION ID #0=(\d+)', line)

                if match:
                    tmp_base = match.group(1)

                if match2:
                    tmp_incr = match2.group(1)

                if tmp_base and tmp_incr:
                    cid[id] = (tmp_base,tmp_incr)

            if cid[id][0] == "" or cid[id][1] == "":
                print("Err on " + str(id))
                exit(-1)

    if not len(cid) == 0:

        time_diff = []
        time_average = 0
        try:
            socket = MySQLdb.connect(tset.HOST, tset.DB_USER, tset.DB_PASSWD, "IrmaDB_prod")
            cursor = socket.cursor()

            for c in cid.keys():

                query = "SELECT compilation_time FROM Compilations WHERE cid = " + cid[c][0]
                cursor.execute(query)
                entry_base = cursor.fetchone()[0]

                query = "SELECT compilation_time FROM Compilations WHERE cid = " + cid[c][1]
                cursor.execute(query)
                entry_incr = cursor.fetchone()[0]

                diff = float(entry_base) - float(entry_incr)

                time_diff.append(diff) # Size of kernel column

        except Exception as e:
            raise
        finally:
            cursor.close()
            socket.close()

        for t in time_diff:
            time_average += t

        time_average /= len(time_diff)

        return time_diff, time_average

    else:
        print("Failed to retrieves CID")
        return []


def diff_size(n):

    number = n
    err = []

    if number > max_number:
        number = max_number
    elif number < 0:
        number = max_number

    print("Number of comparisons:", number, flush=True)

    diff = {}

    for i in range(number):

        print("Number: " + str(i) + " ", flush=True, end='')
        subprocess.run('./bloat-o-meter compare/' + str(i) + '/incr-vmlinux compare/' + str(i) + '/basic-vmlinux > compare/' + str(i) + '/diff_size.txt', shell=True, stdout=open("compare/" + str(i) + "/diff_size.txt",'w'), stderr=subprocess.DEVNULL)

        with open("compare/" + str(i) + "/diff_size.txt", "r") as f:
            lines = f.readlines()
            tmp = lines[-1].split()[-1]
            if not (tmp == "-100.00%" or tmp == "+100.00%"):
                diff[str(i)] = tmp
                print(tmp, flush=True)
            else:
                print('---ERR---', flush=True)
                err.append(str(i))

    # print("Percentage of differences between incremental and basic compiled kernels:")
    liste = list(diff.values())
    # print(liste)

    temp = 0.0
    for i in range(len(liste)):
        temp += float(liste[i][1:-1])

    # if len(liste) == 0:
    average = str(temp/len(liste))[:6] + '%' if not len(liste) == 0 else "No values"
    # print("average difference:", average, flush=True)
    return err, average

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("number", type=int, help="The number of comparisons to do (all by default)", nargs='?', default=-1)
    parser.add_argument("--size", help="Activate the comparisons in size", action="store_true")
    parser.add_argument("--time", help="Activate the comparisons in time", action="store_true")
    parser.add_argument("--all", help="Activate all the comparisons", action="store_true")
    args = parser.parse_args()

    if args.size:
        err,average = diff_size(args.number)
        print("Error on: ", err)
        print("Average:", average)

    elif args.time:
        time_diff, time_average = diff_time(args.number)
        print("time_diff:", time_diff)
        print("time_average:", time_average)

    elif args.all:
        err,average = diff_size(args.number)
        print("Error on: ", err)
        print("Average:", average)

        time_diff, time_average = diff_time(args.number)
        print("time_diff:", time_diff)
        print("time_average:", time_average)

    else:
        parser.print_help()
