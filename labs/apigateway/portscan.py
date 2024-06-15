import argparse
import json
import requests

from test_url import check_url

ports = [21,22,23,53,80,110,111,135,139,143,443,445,993,995,1433,1521,1723,3306,3389,5000,5432,5900,6379,8000,8001,8055,8080,8443,9000]

print("Port Scan for localhost:")
print()

for p in ports:
	url = f"http://localhost:{p}"
	res = check_url(url)
	if res:
		print(f"{p}\tOPEN")
	else:
		print(f"{p}\tCLOSED")