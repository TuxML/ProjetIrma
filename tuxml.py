#!/usr/bin/python

import os
import sys
import subprocess
import re


# author : LE FLEM Erwan, MERZOUK Fahim
#
# [checking_dependencies description]
#
# return value :
#   0
#   1
def checking_dependencies():
    print("[*] Checking dependencies")
    # TODO


# author : LE  LURON Pierre
#
# [sending_data description]
#
# return value :
#   0
#   1
def sending_data():
    print("[*] Sending config file to database")
    # TODO


# author : LEBRETON Mickael
#
# [log_analysis description]
#
# return value :
#   0 the program was able to find the missing package(s)
#   1 it wasn't able to find them
def log_analysis():
    print("[*] Analyzing error log file")

    missing_files = []
    for line in open(PATH + ERR_LOG_FILE, "r"):
        if re.search("fatal error", line):
            missing_files.append(line.split(":")[4])

    if len(missing_files) > 0:
        for f in missing_files:
            # TODO faire apt-file search/pacman -Fo etc
            # puis installer le paquet
            print("\t--> Installing {}".format(f))

        print("[+] Some missing packages were found and installed : restarting compilation")
        return 0
    else:
        print("[-] Unable to find the missing package(s)")
        return 1


# author : LEBRETON Mickael
#
# [compilation description]
#
# return value :
#   0 no error
#   1 compilation has failed but the program was able to find the missing package(s)
#   2 compilation has failed and the program wasn't able to find the missing package(s)
#     (it means an unknow error)
def compilation():
    print("[*] Waiting for compilation ending...");

    if not os.path.exists(PATH + LOG_DIR):
        os.makedirs(PATH + LOG_DIR)

    with open(PATH + STD_LOG_FILE, "w") as std_logs, open(PATH + ERR_LOG_FILE, "w") as err_logs:
        status = subprocess.call(["make", "-C", PATH, "-j", "6"], stdout=std_logs, stderr=err_logs)

    if status == 0:
        print("[+] Compilation done")
        return 0
    else:
        print("[-] Compilation failed, exit status : {}".format(status))
        return log_analysis() + 1


# === MAIN FUNCTION ===
if len(sys.argv) < 2:
    print("[!] USE : ./tuxml.py <path/to/the/linux/sources/directory>")
    sys.exit(-1)

PATH = sys.argv[1]
LOG_DIR = "/logs"
STD_LOG_FILE = LOG_DIR + "/std.logs"
ERR_LOG_FILE = LOG_DIR + "/err.logs"

checking_dependencies()

while compilation():
    pass

if compilation == 0:
    sending_data()
else:
    print("[-] Unable to compile using this .config file or another error append")
