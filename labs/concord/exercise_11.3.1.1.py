import requests

key = "vyblrnt+hP8GNVOfSl9WXgGcQZceBhOmcyhQ0alyX6Rs5ozQbEvChU9K7FWSe7cf"

# yml = f"""
# configuration:
#   dependencies:
#   - "mvn://org.python:jython-standalone:2.7.2"

# flows:
#   default:
#   - script: python
#     body: |
#       print("Whoami")
#   - log: \"Hello, ${{crypto.decryptString('{key}')}}\"
# """

yml = """
flows:
  default:
  - log: "Hello"
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

r = s.post(target, headers=headers, files=files)

print(r.text)