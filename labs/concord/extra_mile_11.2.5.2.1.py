# Script to help generate SQL commands
from hashlib import sha256
import base64

def decode_b64(data):
	# Check for missing padding
	while len(data) % 4 != 0:
		data += '='
	return base64.b64decode(data.encode())

newUserCommand = (
	"INSERT INTO users (user_id, username, is_admin, user_type, is_disabled)\n"
	"VALUES ('acc17a02-b471-46af-9914-48cba3dd3100', 'newuser', 't', 'LOCAL', 'f');"
)

newApikey = "C9gUfB0XR3ZeR8/VWXgWNtxUoEVioBXGMmLOGua7bpI"

newApiKeyCommand = (
	"INSERT INTO api_keys (key_id, api_key, user_id)\n"
	f"VALUES ('9d045030-a474-11eb-b4ab-0242ac120000', '{newApikey}', 'acc17a02-b471-46af-9914-48cba3dd3100');"
)

print(newApiKeyCommand)
print(newUserCommand)
# print(encodedkey)