#!/usr/bin/python3

import argparse
import MySQLdb
import sys
import os
import subprocess
import tuxml_settings as tset
import tuxml_common as tcom


CONFIG_IDS = []
PATH = os.path.dirname(os.path.abspath(__file__))
SOURCE_PATH = ""
CONFIG_PATH = PATH + "/files"

# author : LEBRETON Mickael
#
# This function handles the arguments of the ./inctests.py command
def args_handler():
    global CONFIG_IDS, SOURCE_PATH

    msg = "TODO/"

    p_help = "path to the Linux source directory"
    c_help = "config IDs from the database"
    s_help = "choose on which database download the compilation results"

    parser = argparse.ArgumentParser(description=msg, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("source_path", help=p_help)
    parser.add_argument("config_ids",  help=c_help, type=int, nargs='+')
    parser.add_argument("--database",  help=s_help, type=str, default='prod', choices=['prod', 'dev'])
    args = parser.parse_args()

    # setting up the database
    tset.DB_NAME += args.database

    SOURCE_PATH = args.source_path
    CONFIG_IDS = args.config_ids


def download_kconfig_files():
    tcom.pprint(2, "Downloading kconfig files")

    try:
        socket = MySQLdb.connect(tset.HOST, tset.DB_USER, tset.DB_PASSWD, tset.DB_NAME)
        cursor = socket.cursor()

        values = ','.join(['%s'] * len(CONFIG_IDS))
        query  = 'SELECT config_file, cid FROM Compilations WHERE cid IN ({})'.format(values)

        cursor.execute(query, CONFIG_IDS)
        rows = cursor.fetchall()

        if not os.path.exists(CONFIG_PATH):
            os.makedirs(CONFIG_PATH)

        for row in rows:
            filename = CONFIG_PATH + "/{}.config".format(row[1])
            print(tset.GRAY + " " * 4 + "==> " + filename + ": OK" + tset.WHITE)
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
    tuxml_cmd = PATH + "/tuxml.py " + SOURCE_PATH + " -d " + CONFIG_PATH + "/{}.config --inc-mod {}"

    tcom.pprint(2, "Press any key after changing kconfig options")
    input()

    for cid in CONFIG_IDS:
        print(tuxml_cmd.format(cid, cid))
        subprocess.call([tuxml_cmd.format(cid, cid)], shell=True)

# ============================================================================ #


if __name__ == '__main__':
    main()
