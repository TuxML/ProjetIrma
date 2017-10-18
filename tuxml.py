#!/usr/bin/python3

import os
import sys
import subprocess
import re

# send_data imports
import irma_db
import http.client
import datetime
import json
import base64


# author : LE FLEM Erwan, MERZOUK Fahim
#
# [check_dependencies description]
#
# return value :
#   0
#   1
def check_dependencies():
    print("[*] Checking dependencies")
    # TODO


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
        full_filename = PATH + "/" + filename
        if os.path.isfile(full_filename):
            return os.path.getsize(full_filename)
    return 0


# author : LE LURON Pierre
#
# Sends compilation results to the jhipster db
#
# return value :
#   0 - failed
#   1 - success
def send_data(has_compiled):
    print("[*] Sending config file and status to database")
    # date
    today = datetime.datetime.today()
    dateFormatted = '{0: %Y-%m-%d}'.format(today)
    # Config file
    config_path = PATH + "/.config"
    if not os.path.isfile(config_path):
        print("[-] .config not found")
        return 0

    config_file = open(config_path, "r+b")

    # Error log
    err_log = open(PATH+ERR_LOG_FILE, "r+b").read() if not has_compiled else b""

    try:
        # Initiate HTTP connection 
        conn_http = http.client.HTTPConnection(irma_db.addr)

        # JWT Authentication
        auth_header = {
            'Content-Type':'application/json',
            'Accept':'application/json'
        }

        auth_body = json.dumps(irma_db.user)

        conn_http.request("POST", "/api/authenticate", auth_body, auth_header)
        auth_response = conn_http.getresponse()
        if auth_response.status == 200:
            auth_id  = json.loads(auth_response.read().decode())['id_token']
        else:
            print("[-] db authentication failed : {}".format(auth_response.reason))
            return 0

        # Add an entry
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + auth_id
        }

        post_body = json.dumps({
          "boot": None,
          "boottime": None,
          "compilationtime": None,
          "compile": has_compiled,
          "configfile": (base64.b64encode(config_file.read())).decode(),
          "configfileContentType": "string",
          "coresize": get_kernel_size(),
          "date": dateFormatted,
          "erreur": (base64.b64encode(err_log)).decode(),
          "erreurContentType": "string",
        })

        conn_http.request("POST", "/api/i-rma-dbs", post_body, headers)
        # Status check
        r1 = conn_http.getresponse()
        if r1.status == 201:
            print ("[+] Successfully sent info to db")
            return 1
        else:
            print  ("[-] Can't send info to db : {} - {}".format(r1.status, r1.reason))
            return 0

    except http.client.HTTPException as err:
        if err == http.client.NotConnected: print("[-] Can't connect to db")
        else: print("[-] Unknown db error : {}".format(err))
        return 0


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
def compile():
    print("[*] Waiting for compilation ending...");

    if not os.path.exists(PATH + LOG_DIR):
        os.makedirs(PATH + LOG_DIR)

    with open(PATH + STD_LOG_FILE, "w") as std_logs, open(PATH + ERR_LOG_FILE, "w") as err_logs:
        status = subprocess.call(["make", "-C", PATH, "-j"], stdout=std_logs, stderr=err_logs)

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

check_dependencies()

status = 1
while (status == 1):
    status = compile()

if status == 0:
    print("[+] Successfully compiled, sending data")
else:
    print("[-] Unable to compile using this .config file or another error happened, sending data anyway")

send_data(status == 0)
