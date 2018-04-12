#!/usr/bin/python3

import MySQLdb
import sys
sys.path.insert(0, 'core')
import tuxml_common as tcom
import tuxml_settings as tset
# from core
# import tuxml_common as tcom # , tuxml_settings as tset
# from core import tuxml_environment as tenv
import bz2
import os
import argparse
from sys import argv
import re

# Author Alexis LE MASLE

# Creation of help and argument parser
parser = argparse.ArgumentParser()
parser.add_argument("incremental", help = "The incremental factor (0 by default)", type=int, nargs='?', default=0)
args = parser.parse_args()

#### Send output.log to database with configuration ID (cid)
# eg # send_outputlog(457, "fakeoutput.log", "IrmaDB_prod")
def send_outputlog(cid, outputfilename, databasename):
    try:
        socket = MySQLdb.connect(tset.HOST, tset.DB_USER, tset.DB_PASSWD, databasename) # TODO
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
print("")
print('Running tuxLogs.py ...')
print("")
chaine = '/TuxML/tuxLogs.py ' + str(args.incremental) + ' | tee /TuxML/output.log'
print("")
os.system(chaine)

for line in open('/TuxML/output.log'):
    match = re.search('DATABASE CONFIGURATION ID=(\d+)', line)
    if match:
        cid=match.group(1)
print("CID found " + cid)

send_outputlog(cid, "/TuxML/output.log", "IrmaDB_prod")
