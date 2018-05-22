#!/usr/bin/python3

## @file runandlog.py
# @author LE MASLE Alexis, ACHER Mathieu
# @copyright Apache License 2.0
# @brief Run compilations and update database with logs.
#
# @details This is the program that execute tuxLogs.py in order to run all the compilations
# expected in this container and create the file output.log which contain the complete system output of compilation process.
# This new file output.log is sent to the database through an "UPDATE Compilations SET output_file = %s WHERE cid = %s" command in SQL.
#
# When MLfood.py is called with 10 compilations and 3 as incremental parameter, runandlog is one of the 10 compilations asked,
# which run 1 basic compilation then the 3 incremental compilations.
# The script is run with the command : "./runandlog.py 3" to run 3 incremental compilation in addition to the basic one


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


import MySQLdb
import sys
sys.path.insert(0, 'core')
import tuxml_common as tcom
import tuxml_settings as tset
import bz2
import os
import subprocess
import argparse
import re

# Author Alexis LE MASLE

# Creation of help and argument parser
parser = argparse.ArgumentParser()
parser.add_argument("incremental", help = "The incremental factor (0 by default)", type=int, nargs='?', default=0)
parser.add_argument("--silent", help="No output on standard output", action="store_true")
args = parser.parse_args()

#### Send output.log to database with configuration ID (cid)
# eg # send_outputlog(457, "fakeoutput.log", "IrmaDB_prod")
# Function to send the outputfile to the database at a certain "cid"
def send_outputlog(cid, outputfilename, databasename):
    try:
        socket = MySQLdb.connect(tset.HOST, tset.DB_USER, tset.DB_PASSWD, databasename)
        cursor = socket.cursor()

        bzoutput = bz2.compress(open(outputfilename, "rb").read())

        query = "UPDATE Compilations SET output_file = %s WHERE cid = %s"
        data = (bzoutput, cid)
        cursor.execute(query, data)

        socket.commit()
        socket.close()
        return cid

    except MySQLdb.Error as err:
        tcom.pprint(1, "Can't send info to db : {}".format(err))
        return -1

# Run tuxLogs.py and retrieves the output converted in a log file.
if not args.silent:
    print("")
    print('------ Running runandlog.py ... ------')
    print("")

chaine = ""
# Use to compute only, no standard output, all in the log file
if args.silent:
    chaine = '/TuxML/tuxLogs.py ' + str(args.incremental) + ' > /TuxML/output.log'
else:
    chaine = '/TuxML/tuxLogs.py ' + str(args.incremental) + ' | tee /TuxML/output.log'

print("")
subprocess.run(chaine, shell=True).stdout

if not args.silent:
    print("Removing colors in output file ...")

with open("/TuxML/output.log", 'r+') as f:
    file = f.read()

    escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
    res = escape.sub("", file)

    f.write(res)

if not args.silent:
    print("Try to send output.log ...")

# tuxLogs.py has finished to run, output.log exist now
cid = -1
for line in open('/TuxML/output.log'):
    match = re.search('DATABASE CONFIGURATION ID=(\d+)', line)
    if match:
        cid=match.group(1)
        if not args.silent:
            print("CID found " + cid)

if not cid == -1:
    send_outputlog(cid, "/TuxML/output.log", "IrmaDB_prod")

else:
    print("Cid unfound, no output.log file has been sent")
    print("")
