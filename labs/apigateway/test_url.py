import argparse
import json
import requests
debug = False

def check_url(url):
	target = "http://apigateway:8000/files/import"
	headers = {
		"Content-Type": "application/json"
	}
	data = {
		"url": url
	}

	r = requests.post(target,data=json.dumps(data),headers=headers)

	if r.status_code == 403:
		if debug: print("Resource found at url",url)
		return True
	elif r.status_code == 500:
		if debug: print("Resource not found at url", url)
		return False
	else:
		print("An error has occured")
		return False

def check_ip(ip):
	target = "http://apigateway:8000/files/import"
	headers = {
		"Content-Type": "application/json"
	}
	data = {
		"url": f"http://{ip}"
	}
	r = requests.post(target,data=json.dumps(data),headers=headers)
	# print(r.text)
	text = r.text
	elapsed = r.elapsed.total_seconds()
	
	# print(f"Searching: {ip}")
	# print(text)
	# print(elapsed)

	if elapsed > 30:
		return False
	elif "You don't have permission" in text:
		print("Port open!")
		return True
	elif "ECONNREFUSED" in text: 
		return True
	elif "getaddrinfo" in text:
		return False
	else:
		print("Error")
		print(r.text)
	

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('-u','--url', help='Target url to check')
	args = parser.parse_args()
	url = args.url
	check_ip("127.0.0.1")
	check_ip("192.168.45.205")
	check_ip("192.168.173.135")
	check_ip("244.244.244.244")
	check_ip("277.77.77.77")
	# check_url(url)

if __name__ == '__main__':
	debug = True
	main()