import argparse
import json
import requests

key = "SBzrCb94o9JOWALBvDAZLnHo3s90smjC"
target = "http://apigateway:8000/render?url=http://192.168.45.194/index2.html"

headers = {
  'apikey': key
}

proxies = {
  'http': 'http://127.0.0.1:8080'
}

r = requests.get(target, headers=headers,proxies=proxies)

with open("test.pdf", "w") as f:
  f.write(r.text)