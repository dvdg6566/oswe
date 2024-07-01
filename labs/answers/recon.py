import requests

for i in range(10):
	target = f"http://answers/profile/{i}"
	proxies = {
		'http': 'http://127.0.0.1:8080',
		'https': 'http://127.0.0.1:8080'
	}
	r = requests.get(target, proxies=proxies)

	print(r.status_code)
	print(len(r.content))