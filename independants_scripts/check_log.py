#!/usr/bin/env python3

import MySQLdb
import bz2
import argparse
import subprocess


def get_errlog():
    pass


def main(args):

    subprocess.run("mkdir -p decoded/", shell=True)

    HOST = "148.60.11.195"
    DB_USER = "script2"
    DB_PASSWD = "ud6cw3xNRKnrOz6H"
    DB_NAME = "IrmaDB_prod"

    with MySQLdb.connect(HOST, DB_USER, DB_PASSWD, DB_NAME) as cursor:
        if args.max_cid:
            cursor.execute("SELECT max(cid) FROM Compilations")
            max_cid = cursor.fetchone()
            print("The maximum cid is", max_cid[0])
            return max_cid

        else:
            cursor.execute(
                "SELECT cid, " + args.mode + "_file FROM Compilations WHERE cid >= %s and cid < %s", (args.From, args.To))
            files_coded = cursor.fetchall()
            files = {}
            for x in files_coded:
                tmp = bz2.decompress(x[1]).decode()

                if len(tmp) == 0:
                    continue

                if tmp.partition("Cyclomatic Complexity")[1] == "":
                    files[x[0]] = tmp
                else:
                    files[x[0]] = "Cyclomatic Complexity Error (shortened)"

            with open("decoded/" + str(args.mode) + "_" + str(args.From) + "to" + str(args.To) + ".txt", "w") as file:

                for cid in files:
                    file.write("cid: " + str(cid) + "\n")
                    file.write(files[cid])
                    file.write("\n\n")


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "From", type=int, help="From cid number \"from\" include")
    parser.add_argument("To", type=int, help="To cid number \"To\" exclude")
    parser.add_argument(
        "--max-cid", help="Maximum cid in database", action="store_true")
    parser.add_argument("mode", help="Choose the file you want to decode from database",
                        choices=["output", "err", "std", "config"])
    args = parser.parse_args()

    if args.From < 0:
        args.From = 0

    if args.To < 0:
        args.To = 0

    if args.From > args.To:
        args.From, args.To = args.To, args.From

    if args.mode == "std":
        args.mode = "stdlog"
    if args.mode == "err":
        args.mode = "errlog"

    tot = args.To - args.From
    print("You choose to check for", tot, args.mode, "logs.")

    main(args)
