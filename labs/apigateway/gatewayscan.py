import argparse
import json
import requests

from test_url import check_ip

print("IP Gateway scan for sunet 172.16.0.0/12:")
print()

A = []

# check_ip("172.16.16.1")
# for a in range(16,32):
# 	for b in range(1,256):
# 		ip = f"172.{a}.{b}.1"

for i in range(1,256):
	ip = f"172.16.16.{i}"
	res = check_ip(ip)
	if res:
		print(f"{ip}\tOPEN")
		A.append(ip)
	else:
		print(f"{ip}\tCLOSED")