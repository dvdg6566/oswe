import requests

with open("routes_clean.txt", "r") as f:
	routes = f.read().split('\n')

s = requests.Session()

proxies = {
	'http': 'http://127.0.0.1:8080',
	'https': 'http://127.0.0.1:8080'
}
s.proxies.update(proxies)

for route in routes:
	target = f"http://rudderstack:8080{route}"
	r = s.get(target)
	get_code = r.status_code
	get_size = len(r.content)
	get_text = r.text

	r = s.post(target)
	post_code = r.status_code
	post_size = len(r.content)
	post_text = r.text

	print(target)
	print("GET: ", get_code, get_size)
	print(get_text)
	print("POST: ", post_code, post_size)
	print(post_text)