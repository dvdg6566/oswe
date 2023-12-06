
def reset_password(ip, password_url):
	params = {}
	params_strings = password_url.split('?')[1].split('&')
	for param in params_strings:
		x = param.split('=')
		if len(x) != 2: 
			raise ("Invalid URL!")
		params[x[0]] = x[1]
	
	data = {
		'form_change': 'true',
		'id': params['id'],
		'g': params['g'],
		'h': params['h'], 
		'password': 'Bromine1!',
		'password2': 'Bromine1!',
		'submit': 'Submit'
	}
	

reset_password('x', 'http://atutor/ATutor/password_reminder.php?id=1&g=19697&h=67c5b839df049b9')