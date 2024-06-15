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

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('-u','--url', help='Target url to check')
	args = parser.parse_args()
	url = args.url
	return check_url(url)

if __name__ == '__main__':
	debug = True
	main()