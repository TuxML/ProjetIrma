#!/usr/bin/python3

import irmaDBCredentials
import time
import os
import MySQLdb
import argparse
import base64
import tuxml_common as tcom
import tuxml_settings as tset
import tuxml_environment as tenv


# author : LE LURON Pierre
#
# Returns the size of the newly compiled kernel
#
# return value :
#   0 - can't find kernel image
#   x - size of kernel in bytes
def get_kernel_size():
    possible_filenames = ["vmlinux", "vmlinux.bin", "vmlinuz", "zImage", "bzImage"]
    for filename in possible_filenames:
        full_filename = tset.PATH + "/" + filename
        if os.path.isfile(full_filename):
            return os.path.getsize(full_filename)
    return 0


# author : LE LURON Pierre
#
# Sends compilation results to the mysql db
#
# return value :
#   -1 Fail
#    0 Sucess
def send_data(compile_time):
    tcom.pprint(2, "Sending config file and status to database")

    # Log files
    logfiles = [tset.PATH + "/.config",
                tset.PATH + tset.STD_LOG_FILE,
                tset.PATH + tset.ERR_LOG_FILE]
    for logfile in logfiles:
        if not os.path.isfile(logfile):
            tcom.pprint(1, "{} not found".format(logfile))
            return -1

    try:
        conn = MySQLdb.connect(**irmaDBCredentials.info)
        cursor = conn.cursor()

        # Values for request
        parameters = {
            "compilation_date": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())),
            "compilation_time": str(compile_time),
            "config_file": open(logfiles[0], "r").read(),
            "stdlog_file": open(logfiles[1], "r").read(),
            "errlog_file": open(logfiles[2], "r").read(),
            "core_size": str(get_kernel_size()),
            "dependencies": "",
            "mechanical_drive": '0'
        }

        for dico in tset.TUXML_ENV:
            parameters.update(tset.TUXML_ENV[dico])

        keys   = ",".join(parameters.keys())
        values = ','.join(['%s'] * len(parameters.values()))

        query  = "INSERT INTO Compilations({}) VALUES({})".format(keys, values)

        cursor.execute(query, list(parameters.values()))
        conn.commit()
        conn.close()

        tcom.pprint(0, "Successfully sent info to db")
        return 0
    except MySQLdb.Error as err:
        tcom.pprint(1, "Can't send info to db : {}".format(err))
        return -1


if __name__ == "__main__":
    msg = "TuxML send script - Use only for testss"

    p_help  = "path to the Linux source directory"

    parser = argparse.ArgumentParser(description=msg, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("source_path", help=p_help)

    args = parser.parse_args()

    # store the linux source path in a global var
    if not os.path.exists(args.source_path):
        tcom.pprint(1, "This path doesn't exist")
        sys.exit(-1)
    else:
        tset.PATH = args.source_path

    tset.TUXML_ENV = tenv.get_environment_details()
    send_data(123)
