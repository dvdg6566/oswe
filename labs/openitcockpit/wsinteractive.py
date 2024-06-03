import websocket
import ssl
import json
import argparse
import _thread as thread # To allow for execution of tasks in background
uniqid = ""
key = ""

def toJson(task,data):
	req = {
		"task": task,
		"data": data,
		"uniqid": uniqid,
		"key": key
	}
	return json.dumps(req)

def on_open(ws):
	print("[+] Connection Open")
	def run():
		cmd = input()
		ws.send(toJson("execute_nagios_command", cmd))
	thread.start_new_thread(run, ())

def on_message(ws, message):
	global uniqid
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

def on_error(ws, error):
	print()
	print("Error: ", error)

def on_close(ws, close_status_code, close_msg):
	print()
	print("[+] Connection Closed")
	print(close_msg)

def main(args):
	global key
	key = args.key
	url = args.url
	# print(url)
	websocket.enableTrace(args.verbose)
	ws = websocket.WebSocketApp(args.url,
		on_message = on_message,
		on_error= on_error,
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
