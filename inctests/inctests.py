#!/usr/bin/python3

import argparse
import MySQLdb
import sys
import os
sys.path.append("../core")
import tuxml_settings as tset
import tuxml_common as tcom

CONFIG_IDS = []

# author : LEBRETON Mickael
#
# This function handles the arguments of the ./inctests.py command
def args_handler():
    global CONFIG_IDS

    msg = "TODO/"

    c_help = "config IDs from the database"
    s_help = "choose on which database download the compilation results"

    parser = argparse.ArgumentParser(description=msg, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("cids",       help=c_help, type=int, nargs='+')
    parser.add_argument("--database", help=s_help, type=str, default='prod', choices=['prod', 'dev'])
    args = parser.parse_args()

    # setting up the database
    tset.DB_NAME += args.database

    CONFIG_IDS = args.cids

def download_kconfig_files():
    tcom.pprint(2, "Downloading kconfig files")

    try:
        socket = MySQLdb.connect(tset.HOST, tset.DB_USER, tset.DB_PASSWD, tset.DB_NAME)
        cursor = socket.cursor()

        values = ','.join(['%s'] * len(CONFIG_IDS))
        query  = 'SELECT config_file, cid FROM Compilations WHERE cid IN ({})'.format(values)

        cursor.execute(query, CONFIG_IDS)
        rows = cursor.fetchall()

        if not os.path.exists("./files"):
            os.makedirs(os.path.dirname(os.path.abspath(__file__)) + "/files")

        for row in rows:
            filename = "./files/{}.config".format(row[1])
            print(tset.GRAY + " " * 4 + "==> " + filename + ": OK")
            with open(filename, "w") as f:
                f.write(row[0])

        socket.close()

        tcom.pprint(0, "All files were downloaded successfully")
        return 0
    except MySQLdb.Error as err:
        tcom.pprint(1, "Can't select info from db : {}".format(err))
        return -1


def main():
    args_handler()

    download_kconfig_files()

# ============================================================================ #


if __name__ == '__main__':
    main()
