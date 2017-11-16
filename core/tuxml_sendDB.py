import irmaDBCredentials
import http.client
import datetime
import json
import base64
import os

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
# Sends compilation results to the jhipster db
#
# return value :
#   0 - failed
#   1 - success
def send_data(path, err_log_file, compile_time):
    print("[*] Sending config file and status to database")
    # date
    today = datetime.datetime.today()
    dateFormatted = '{0: %Y-%m-%d}'.format(today)
    # Config file
    config_path = path + "/.config"
    if not os.path.isfile(config_path):
        print("[-] .config not found")
        return 0

    config_file = open(config_path, "r+b")

    # Error log
    has_compiled = compile_time > 0
    err_log = open(path+err_log_file, "r+b").read() if not has_compiled else b""

    try:
        # Initiate HTTP connection
        conn_http = http.client.HTTPConnection(irmaDBCredentials.addr)

        # JWT Authentication
        auth_header = {
            'Content-Type':'application/json',
            'Accept':'application/json'
        }

        auth_body = json.dumps(irmaDBCredentials.user)

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
          "coresize": get_kernel_size(path),
          "date": dateFormatted,
          "erreur": (base64.b64encode(err_log)).decode(),
          "erreurContentType": "string",
          "dependance": (base64.b64encode(b"")).decode(),
          "dependanceContentType": "string"
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
