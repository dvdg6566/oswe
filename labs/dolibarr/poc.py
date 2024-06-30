import subprocess
import re

cmd = "php -r \"print_r(get_defined_functions());\""

r = subprocess.run(cmd,capture_output=True, shell=True)
out = r.stdout.decode()

php_funcs = out.split('\n')
# print(len(php_funcs))
exec_ind = -1

for i in php_funcs:
	cmd = i.split(' ')[-1]
	index = re.findall(r'\[(.*)\]', i)
	if "exec" == cmd:
		print(index[0], cmd)
		exec_ind = int(index[0])
# print(r.stderr)

cmd = f"php -r \"echo get_defined_functions()[\'internal\'][\"{exec_ind}\"]('whoami');\""

r = subprocess.run(cmd,capture_output=True, shell=True)
out = r.stdout.decode()

print(out)