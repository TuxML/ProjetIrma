#!/usr/bin/python3

# -*- coding: utf-8 -*-

#   Copyright 2018 TuxML Team
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

## @file tuxml_sendDB.py
#  @author LE LURON Pierre
#  @author LEBRETON Mickaël
#  @copyright Apache License 2.0
#  @brief The file contains the functions used to send compilation and test results
#  to the database


import time
import os
import MySQLdb
import argparse
# import paramiko
import bz2
import tuxml_common as tcom
import tuxml_settings as tset
import tuxml_environment as tenv


## @author  LE LURON Pierre
#
#  @brief   Get the size of the newly compiled kernel
#
#  @returns  0 can't find kernel image
#  @returns >0 size of kernel in bytes
def get_kernel_size():
    possible_filenames = ["vmlinux", "vmlinux.bin", "vmlinuz", "zImage", "bzImage"]
    for filename in possible_filenames:
        full_filename = tset.PATH + "/" + filename
        if os.path.isfile(full_filename):
            return os.path.getsize(full_filename)
    return 0


## @author  LEBRETON Mickaël
#
#  @brief   Function used to upload logfiles on the server with the SFTP protocole
#
#  @param   logfiles table containing path to log files
#  @param   date the date
#
#  @returns -1 can't upload log files on server
#  @returns  0 all files were uploaded successfully
#
#  @warning Currently not in use
def file_upload(logfiles, date):
    tcom.pprint(2, "Uploading log files to server")
    paramiko.util.log_to_file(tset.SFTP_LOGS)

    try:
        transport = paramiko.Transport((tset.HOST, tset.SFTP_PORT))
        transport.connect(username=tset.SFTP_USER, password=tset.SFTP_PASSWD)
        sftp = paramiko.SFTPClient.from_transport(transport)

        remote_dir = time.strftime("%Y%m%d_%H%M%S/", date)
        sftp.mkdir(tset.SFTP_DIR + remote_dir)

        for logfile in logfiles:
            remotepath = tset.SFTP_DIR + remote_dir + os.path.basename(logfile)
            localpath = logfile
            sftp.put(localpath, remotepath)
            if (tset.VERBOSE > 2):
                print(tset.GRAY + " " * 4 + "==> " + localpath + ": OK")

        sftp.close()
        transport.close()

        tcom.pprint(0, "All files were uploaded successfully")
        return 0
    except paramiko.SSHException as err:
        tcom.pprint(1, "Can't upload log files on server : {}".format(err))
        return -1


## @author  LE LURON Pierre
#  @author  LEBRETON Mickaël
#
#  @brief   Sends compilation and boot results to the mysql database
#
#  @param   compile_time compilation time
#  @param   boot_time boot time
#
#  @returns -1 can't send info to db
#  @returns  0 successfully sent info to db
def send_data(compile_time, boot_time):
    tcom.pprint(2, "Sending compilation and test results to database")

    # Log files
    logfiles = [tset.PATH + "/.config",
                tset.PATH + tset.STD_LOG_FILE,
                tset.PATH + tset.ERR_LOG_FILE]

    for logfile in logfiles:
        if not os.path.isfile(logfile):
            tcom.pprint(1, "{} not found".format(logfile))
            return -1

    try:
        socket = MySQLdb.connect(tset.HOST, tset.DB_USER, tset.DB_PASSWD, tset.DB_NAME)
        cursor = socket.cursor()

        # Values for request
        date = time.gmtime(time.time())
        args = {
            "compilation_date": time.strftime("%Y-%m-%d %H:%M:%S", date),
            "compilation_time": str(compile_time),
            # "config_file": time.strftime("%Y%m%d_%H%M%S", date) + "/.config",
            # "stdlog_file": time.strftime("%Y%m%d_%H%M%S", date) + "/std.log",
            # "errlog_file": time.strftime("%Y%m%d_%H%M%S", date) + "/err.log",
            "config_file": bz2.compress(open(logfiles[0], "rb").read()),
            "stdlog_file": bz2.compress(open(logfiles[1], "rb").read()),
            "errlog_file": bz2.compress(open(logfiles[2], "rb").read()),
            "core_size": str(get_kernel_size()),
            "dependencies": "",
        }

        for dico in tset.TUXML_ENV:
            args.update(tset.TUXML_ENV[dico])

        keys   = ",".join(args.keys())
        values = ','.join(['%s'] * len(args.values()))

        query  = "INSERT INTO Compilations({}) VALUES({})".format(keys, values)
        cursor.execute(query, list(args.values()))

        query = "SELECT cid FROM Compilations ORDER BY cid DESC LIMIT 1"
        cursor.execute(query)
        cid = cursor.fetchone()[0]

        if tset.INCREMENTAL_MOD and tset.BASE_CONFIG_ID != 0:
            query  = "INSERT INTO Incremental_compilations(cid_incmod, cid_origin) VALUES (%s, %s)"
            cursor.execute(query, [cid, tset.BASE_CONFIG_ID])

        query  = "INSERT INTO Tests(cid, test_date, boot_time) VALUES (%s, %s, %s)"
        cursor.execute(query, [cid, time.strftime("%Y-%m-%d %H:%M:%S", date), boot_time])

        socket.commit()
        socket.close()

        # file_upload(logfiles, date)

        tcom.pprint(0, "Successfully sent info to db")
        return cid
    except MySQLdb.Error as err:
        tcom.pprint(1, "Can't send info to db : {}".format(err))
        return -1


# ============================================================================ #


if __name__ == "__main__":
    # msg = "TuxML send script - Use only for testss"
    #
    # p_help  = "path to the Linux source directory"
    #
    # parser = argparse.ArgumentParser(description=msg, formatter_class=argparse.RawTextHelpFormatter)
    # parser.add_argument("source_path", help=p_help)
    #
    # args = parser.parse_args()
    #
    # # store the linux source path in a global var
    # if not os.path.exists(args.source_path):
    #     tcom.pprint(1, "This path doesn't exist")
    #     sys.exit(-1)
    # else:
    #     tset.PATH = args.source_path
    #
    # tset.VERBOSE = 3
    # tset.DB_NAME = "IrmaDB_dev"
    # tset.INCREMENTAL_MOD = 0
    # tset.CONFIG_ID = 7
    #
    # tset.TUXML_ENV = tenv.get_environment_details()
    # send_data(123, 456)
