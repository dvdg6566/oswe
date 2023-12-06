from bs4 import BeautifulSoup
import re
import html

with open("out.txt", "r") as f:
	text = f.read()

url_matches = re.findall('(http:\\\/\\\/atutor\\\/ATutor\\\/password_reminder.php.*?)&lt;br', text)
url = url_matches[0]
print(url)

url = html.unescape(url)
url = url.replace('&amp;', '&')
url = url.replace(r'\/', r'/')
print(url)
