#!/usr/bin/python3

import irmaDBCredentials
import http.client
import json
import base64
import os
import re

'''
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
        exit(-1)

    # Get all entries
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer ' + auth_id
    }

    conn_http.request("GET", "/api/i-rma-dbs", None, headers)
    # Status check
    r1 = conn_http.getresponse()
    if r1.status == 200:
        print ("[+] Successfully got all data")
        print (r1.read())
    else:
        print  ("[-] Can't get data from db : {} - {}".format(r1.status, r1.reason))
        print (r1.read())

except http.client.HTTPException as err:
    if err == http.client.NotConnected: print("[-] Can't connect to db")
    else: print("[-] Unknown db error : {}".format(err))
    exit(-1)
'''

config_folder = "configs/"

config_files = os.listdir(config_folder)

file_count = len(config_files)

properties = {"KERNEL_SIZE":[0]*file_count}

pattern = re.compile("^([^#][^=]*)=(.*)$")

for file_number, config_file in enumerate(config_files):
    config_content = open(config_folder + config_file, "r")
    # Config properties
    for line in config_content:
        m = re.match(pattern, line)
        if m:
            key = m.group(1)
            value = m.group(2)
            if key not in properties:
                properties[key] = ["n"]*file_count
            properties[key][file_number] = value
    # File size
    properties["KERNEL_SIZE"][file_number] = str(os.path.getsize(config_folder + config_file))

for (k,v) in properties.items():
    values = k
    for va in v:
        values += "," + va

    print(values)


