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
#  @author LE MASLE Alexis
#  @copyright Apache License 2.0
#  @brief The file contains the functions used to send compilation and test results
#  to the database


import time
import os
import MySQLdb
import argparse
import bz2
import tuxml_common as tcom
import tuxml_settings as tset
import tuxml_environment as tenv
import configCompress as compress
import subprocess

## @author  LE LURON Pierre
#
#  @brief   Get the size of the newly compiled kernel
#
#  @returns  0 can't find kernel image
#  @returns >0 size of kernel in bytes
#  @deprecated
def get_kernel_size():
    possible_filenames = ["vmlinux", "vmlinux.bin", "vmlinuz", "zImage", "bzImage"]
    for filename in possible_filenames:
        full_filename = tset.PATH + "/" + filename
        if os.path.isfile(full_filename):
            tcom.pprint(2, "kernel found: " + filename)
            return os.path.getsize(full_filename)
    return 0

## @author LE MASLE Alexis
#
# @brief Get the "vmlinux" size
#
# @details New version of get_kernel_size() which was inaccurate, only get the "vmlinux" size
# without looking for others name possible
#
# @returns 0 can not find the vmlinux file
# @returns >0 size of kernel "vmlinux" in bytes
def get_size_kernel():
    full_filename = tset.PATH + "/vmlinux"
    if os.path.isfile(full_filename):
        tcom.pprint(2, "kernel found: vmlinux")
        return os.path.getsize(full_filename)
    return 0




## @author LE MASLE Alexis
#
# @brief Get the size of the 18 differents compressed kernels
#
# @returns The string formated as "compressed_name_1 : size1 , compressed_name_2 : size2 ..."
# @returns "compressed_name_1 : 0 , compressed_name_2 : 0 ..." when no compressed_sizes could be found
def get_compressed_sizes():
    compression = ["GZIP","BZIP2","LZMA","XZ","LZO","LZ4"]
    extension = [".gz", ".bz2", ".lzma", ".xz", ".lzo", ".lz4"]
    res = ""

    for c in compression:
        if compress.enable(c, tset.PATH) == -1:
            if res == "":
                res = res + c + " : 0"
            else:
                res = res + " , " + c + " : 0"
        else:
            subprocess.run("make -C " + tset.PATH + " -j " + str(tset.NB_CORES), shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            size = subprocess.check_output("wc -c " + tset.PATH + "/arch/x86/boot/compressed/*" + extension[compression.index(c)], shell=True, stderr=subprocess.DEVNULL).decode().replace("\n", "").split()[0]
            vm = subprocess.check_output("wc -c " + tset.PATH + "/arch/x86/boot/compressed/vmlinux", shell=True, stderr=subprocess.DEVNULL).decode().replace("\n", "").split()[0]
            bzImage = subprocess.check_output("wc -c " + tset.PATH + "/arch/x86/boot/bzImage", shell=True, stderr=subprocess.DEVNULL).decode().replace("\n", "").split()[0]

            if size == "":
                size = "0"
            if vm == "":
                vm = "0"

            if res == "":
                res = res + c + "-bzImage : " + bzImage + " , " + c + "-vmlinux : " + vm + " , " + c + " : " + size
            else:
                res = res + " , " + c + "-bzImage : " + bzImage + " , " + c + "-vmlinux : " + vm + " , " + c + " : " + size

    return res




## @author  LE LURON Pierre
#  @author  LEBRETON Mickaël
#  @author  LE MASLE Alexis
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
            "config_file": bz2.compress(open(logfiles[0], "rb").read()),
            "stdlog_file": bz2.compress(open(logfiles[1], "rb").read()),
            "errlog_file": bz2.compress(open(logfiles[2], "rb").read()),
            "core_size": str(get_size_kernel()),
            "compressed_sizes": get_compressed_sizes(),
            "dependencies": open("dependences.txt", "r").read()
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


#if __name__ == "__main__":
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
