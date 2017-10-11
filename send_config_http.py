#!/usr/bin/python3

import http.client
import json
import base64
import irma_db
import datetime

today = datetime.datetime.today()
dateFormatted = '{0:%Y-%m-%d}'.format(today)

try:
	conn_http = http.client.HTTPConnection(irma_db.addr)

	# Authentification
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
		print("Auth failed : " + auth_response.reason)
		sys.exit(-1)

	headers = {
		'Content-Type': 'application/json',
		'Accept': 'application/json',
		'Authorization': 'Bearer ' + auth_id
	}

	post_body = json.dumps({
	  "boot": True,
	  "boottime": 0,
	  "compilationtime": 0,
	  "compile": True,
	  "configfile": (base64.b64encode(b"ceci est un test")).decode(),
	  "configfileContentType": "string",
	  "coresize": 0,
	  "date": dateFormatted,
	  "erreur": (base64.b64encode(b"ceci est un test")).decode(),
	  "erreurContentType": "string",
	})

	# Créer une entrée
	conn_http.request("POST", "/api/i-rma-dbs", post_body, headers)
	r1 = conn_http.getresponse()
	print (r1.status, r1.reason, r1.read())

	# Récupérer toutes les entrées
	conn_http.request("GET", "/api/i-rma-dbs", None, headers)
	r1 = conn_http.getresponse()
	print(r1.status, r1.reason, r1.read())

	conn_http.close()
except http.client.HTTPException as err:
	if err == http.client.NotConnected: print("Can't connect")
	else: print(err)
	sys.exit(-1)