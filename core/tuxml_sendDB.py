#!/usr/bin/python3

import irmaDBCredentials
import datetime
import os
import MySQLdb
import tuxml_common as tcom

# author : LE LURON Pierre
#
# Returns the size of the newly compiled kernel
#
# return value :
#   0 - can't find kernel image
#   x - size of kernel in bytes
def get_kernel_size(path):
    possible_filenames = ["vmlinux", "vmlinux.bin", "vmlinuz", "zImage", "bzImage"]
    for filename in possible_filenames:
        full_filename = path + "/" + filename
        if os.path.isfile(full_filename):
            return os.path.getsize(full_filename)
    return 0

# author : LE LURON Pierre
#
# Sends compilation results to the mysql db
#
# return value :
#   0 - failed
#   1 - success
def send_data(path, err_log_file, compile_time):
    tcom.pprint(2, "Sending config file and status to database")
    # date
    today = datetime.datetime.today()
    dateFormatted = '{0:%Y-%m-%d}'.format(today)
    # Config file
    config_path = path + "/.config"
    if not os.path.isfile(config_path):
        tcom.pprint(1, ".config not found")
        return 0

    config_file = open(config_path, "r+b")

    # Error log
    has_compiled = compile_time > 0
    err_log = open(path+err_log_file, "r+b").read() if not has_compiled else ""

    try:
        conn = MySQLdb.connect(**irmaDBCredentials.info)
        cursor = conn.cursor()

        # Request
        entry_sql = ("INSERT INTO TuxML"
            "(compilation_time, config_file, core_size, error)"
            "VALUES (%(compilation_time)s, %(config_file)s, %(core_size)s, %(error)s)")

        # Values for request
        entry_values = {
            "compilation_time": compile_time,
            "config_file": config_file.read(),
            "core_size": get_kernel_size(path),
            "date": dateFormatted,
            "error": err_log
        }

        cursor.execute(entry_sql, entry_values)
        conn.commit()

        tcom.pprint(0, "Successfully sent info to db")
        return 1

    except MySQLdb.Error as err:
        tcom.pprint(1, "Can't send info to db : {}".format(err.args[1]))
    finally:
        conn.close()

    return 0

# Tests
# Don't do this if you're not me
if __name__ == "__main__":
    send_data("../../kernel/linux-4.13.3/", "err.logs", 530)
