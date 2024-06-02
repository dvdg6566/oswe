# Dumps all contents of .db files in /db directory into regular files

# cookies
# credentials
# html_pages

# Cookies and credentials should be compiled into json files
# html pages should be extracted as individual files

import os
import json
from db import *
os.chdir('db')

from secrets import token_hex
contentDir = os.getcwd() + "/export-" + token_hex(4) + "/"
os.mkdir(contentDir)
html_pages = sqlDB('html_pages.db')
cookies = sqlDB('cookies.db')
credentials = sqlDB('credentials.db')

# Expand out URL and write out html file
def write_to_file(url, content):
	fileName = url.replace('https://', '')
	if not fileName.endswith(".html"):
		fileName += ".html"
	fullname = os.path.join(contentDir, fileName)
	path, basename = os.path.split(fullname)
	if not os.path.exists(path):
		os.makedirs(path)
	with open(fullname, 'w') as f:
		f.write(content)
	print(fullname)
	print(url)

def main():
	locations = cookies.get_locations()
	for l in locations:
		content = cookies.get_content((l,))[0]
		with open(contentDir + "cookies.json", "a") as f:
			f.write(content)

	locations = credentials.get_locations()
	for l in locations:
		content = credentials.get_content((l,))[0]
		with open(contentDir + "credentials.json", "a") as f:
			f.write(content)
			f.write('\n')

	locations = html_pages.get_locations()
	for l in locations:
		content = html_pages.get_content((l,))[0]
		write_to_file(l, content)

if __name__ == '__main__':
	main()