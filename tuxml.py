#!/usr/bin/python3

# compile, log analysis & dependencies imports
import os
import sys
import subprocess
import re
import shutil
import time

# send_data imports
import irma_db
import http.client
import datetime
import json
import base64


# === GLOBALS ===
PATH = ""
LOG_DIR = "/logs"
STD_LOG_FILE = LOG_DIR + "/std.logs"
ERR_LOG_FILE = LOG_DIR + "/err.logs"
DISTRO = ""
DEBUG = False
COUNTER = 0 # number of time the program had to recompile


# author : LEBRETON Mickael
#
# Get the package manager of the system
#
# return value :
#  -1 Distro not supported
#   0 Arch based distro
#   1 Debian based distro
#   2 RedHat based distro
def get_distro():
    package_managers = ["pacman", "apt-get", "dnf"]
    for pm in package_managers:
        try:
            distro = package_managers.index(shutil.which(pm).split("/")[3]) #/usr/bin/pacman --> pacman
        except Exception as err:
            distro = -1

        if 0 <= distro and distro < len(package_managers):
            return distro
    return -1


# author : LE FLEM Erwan, MERZOUK Fahim
#
# [check_dependencies description]
#
# return value :
#   0
#   1
def check_dependencies():
    print("[*] Checking dependencies")
    # TODO check_dependencies


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
def send_data(compile_time):
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
    has_compiled = compile_time > 0
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
          "compilationtime": compile_time,
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
# [install_missing_packages description]
#
## return value :
#   -1 distro not supported by TuxML
#    0 installation OK
def install_missing_packages(missing_files, missing_packages):
    # 0 Arch / 1 Debian / 2 RedHat
    if DISTRO > 2:
        print("[-] Distro not supported by TuxML")
        return -1

    if DEBUG:
        if DISTRO == 0:
            print("=== Arch based distro")
        elif DISTRO == 1:
            print("=== Debian based distro")
        elif DISTRO == 2:
            print("=== RedHat based distro")
        else:
            pass

    cmd_update = ["pacman -Sy", "apt-file update && apt-get update"]
    cmd_search = ["pkgfile -s {} | grep {}", "apt-file search {} | grep {}"]
    cmd_install = ["pacman --noconfirm -S ", "apt-get -y install "]

    if DEBUG:
        print("=== Those files are missing :")

    for mf in missing_files:
        # example : mf = "openssl/bio.h"
        if DEBUG:
            print("===" + mf)

        output = subprocess.check_output([cmd_search[DISTRO].format(mf.split("/")[1], mf.split("/")[0])], shell=True)

        # some times the output gives several packages, the program takes the first one (== first line)
        line = output.decode("utf-8").splitlines()
        missing_packages.append(line[COUNTER].split(":")[0]) #debian and archway

    print("[*] Updating package database")
    subprocess.call([cmd_update[DISTRO]], shell=True)

    print("[*] Installing missing packages : " + " ".join(missing_packages))
    subprocess.call([cmd_install[DISTRO] + " ".join(missing_packages)], shell=True)
    # BUG Des fois le gestionnaire de paquet ne trouve pas le paquet
    # Donc l'install des paquets plante mais la compile recommence
    # (cas de aicdb.h)

    return 0


# author : LEBRETON Mickael
#
# [log_analysis description]
#
# return value :
#   -1 it wasn't able to find them
#    0 the program was able to find the missing package(s)
def log_analysis():
    global COUNTER

    print("[*] Analyzing error log file")

    missing_files = []
    missing_packages = []
    with open(PATH + ERR_LOG_FILE, "r") as err_logs:
        for line in err_logs:
            if re.search("fatal error", line):
                # case "file.c:48:19: fatal error: <file.h>: No such file or directory"
                missing_files.append(line.split(":")[4])
            elif re.search("Command not found", line):
                # case make[4]: <package> : command not found
                missing_packages.append(line.split(":")[1])
            elif re.search("not found", line):
                # case /bin/sh: 1: <package>: not found
                missing_packages.append(line.split(":")[4])
            else:
                pass

    if len(missing_files) > 0 or len(missing_packages) > 0:
        status = install_missing_packages(missing_files, missing_packages)

        if status == 0:
            print("[+] Restarting compilation")
            COUNTER += 1
            return 0
        else:
            return -1
    else:
        print("[-] Unable to find the missing package(s)")
        return -1


# author : LEBRETON Mickael
#
# [compilation description]
#
# return value :
#   -1 compilation has failed but the program was able to find the missing package(s)
#   -2 compilation has failed and the program wasn't able to find the missing package(s)
#      (it means an unknow error)
#   >0 no error (time to compile in seconds)
def compile():
    print("[*] Compilation in progress");
    # barre de chargement [ ##########-------------------- ] 33%

    if not os.path.exists(PATH + LOG_DIR):
        os.makedirs(PATH + LOG_DIR)

    with open(PATH + STD_LOG_FILE, "w") as std_logs, open(PATH + ERR_LOG_FILE, "w") as err_logs:
        start_time = time.time()
        status = subprocess.call(["make", "-C", PATH, "-j", "6"], stdout=std_logs, stderr=err_logs)
        end_time = time.time()

    if status == 0:
        print("[+] Compilation done")
        return end_time - start_time
    else:
        print("[-] Compilation failed, exit status : {}".format(status))
        return log_analysis() - 1


# === MAIN FUNCTION ===
if len(sys.argv) < 2 or os.getuid() != 0:
    print("[*] USE : ./tuxml.py <path/to/the/linux/sources/directory> [option1 option2 ...]")
    print("[*] Please run TuxML as root")
    print("[*] Available options :")
    print("\t--debug\t\tTuxML is more verbose and do not generate a new config file")
    sys.exit(-1)

PATH = sys.argv[1]
DISTRO = get_distro()

if "--debug" in sys.argv:
    DEBUG = True
    print("=== Debug mode enabled")
    print("[*] Cleaning previous compilation")
    subprocess.call(["make", "clean"])
else:
    DEBUG = False
    print("[*] Cleaning previous compilation")
    subprocess.call(["make", "mrproper"])
    print("[*] Generating random config")
    subprocess.call(["make", "-C", PATH, "randconfig"])

check_dependencies()

status = -1
while (status == -1):
    if DEBUG:
        print("=== Counter : {}".format(COUNTER))
    status = compile()

if status >= 0:
    print("[+] Testing the kernel config")
    print("[+] Successfully compiled in " + time.strftime("%H:%M:%S", time.gmtime(status)) + ", sending data")
else:
    # status == -2
    print("[-] Unable to compile using this config or another error happened, sending data anyway")

send_data(status)
