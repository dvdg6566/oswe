# Routing and Architecture

## Model-View-Controller (MVC)

Separate design pattern into 3 components to help increase reusability

- Controller handles input received from user (HTTP route or parameter), and maps input to functions to be executed. Handles all user input logic.
- Model maps data to specific object and defines object to process data. Model object variables commonly match columns found in database table.
- View is final output rendered to user (HTML, XML, etc.). The controller then renders a view using data and responds back to the user.

Frappe framework and ERPNext application follow MVC design pattern. Doctype is the basic building block of application and encompasses all 3 MVC elements. 

## Metadata-drive design patterns

Metadata-drive pattern creates layer of abstraction and work well for generic database-drive applications that allows users to **customize stored data**. 

- Application generates necessary components to manage (CRUD) databases based on metadata
- Doctypes helps developers reuse single full-featured application for multiple types of industries
- Frappe kernel grabs and parses Doctypes to create appropriate tables in database. Common goal is to allow for creation of metadata documents via GUI

Going to the application and searching for Doctype allows us to view the list of Doctypes and inspect each of their details. Programmatically, we can find them in `apps/erpnext/erpnext/stock/doctype/<name>`. 

- Within each folder, the DocType will contain a JSON file which directly defines that data stored, while a `.py` file contains additional logic and routes for more features. For instance, `bank_account` contains a python script that adds 3 functions, `make_bank_account`, `get_party_bank_account` and `get_bank_account_details`.

As such, Doctype encompasses all 3 models of the MVC: Model with a table in database, view with ability to be edited and displayed as a form, and controller by making use of `.py` accompanying files. 

## HTTP routing in Frappe

Frappe uses a Python **decorator** with the function name whitelist to expose API endpoints. Similar to Flask’s `@app.route`, when a function has the term `@frappe.whitelist()` decorator above it, the whitelist function is executed, and the function calls is added to a list of whitelisted functions. The list is then used by the handler found in `handler.py`, which handles and processes HTTP requests.

When frappe checks whether a function is whitelisted, it simply checks that it’s in the whitelisted array of functions. As such, te client can call **any Frappe function directly** if the `@frappe.whitelist` decorator is used for that function. Additionally, if `allow_guest=True` is passed in the decorator, the user **does not have to be authenticated** to run that function.

When frappe receives a request, it extracts the `cmd` parameter and executes it, as long as the command is not “login”

```python
def handle():
	"""handle request"""
	cmd = frappe.local.form_dict.cmd
	data = None

	if cmd!='login':
		data = execute_cmd(cmd)
```

Within the `execute_cmd` functionality, the code checks that the method is whitelisted, and if so, invokes that specific method as response. 

```python
def execute_cmd(cmd, from_async=False):
	"""execute a request as python module"""
	for hook in frappe.get_hooks("override_whitelisted_methods", {}).get(cmd, []):
		# override using the first hook
		cmd = hook
		break

	try:
		method = get_attr(cmd)
	except Exception as e:
		if frappe.local.conf.developer_mode:
			raise e
		else:
			frappe.respond_as_web_page(title='Invalid Method', html='Method not found',
			indicator_color='red', http_status_code=404)
		return

	if from_async:
		method = method.queue

	is_whitelisted(method)

	return frappe.call(method, **frappe.form_dict)
```

When we open the root page of ERPNext with Burp proxy, we capture a request that attempts to run a Python function directly, using the following command. 

```python
frappe.website.doctype.website_settings.website_settings.is_chat_enabled
```

As such, we can trace the application’s directory structure to find that specific function in `app/frappe/frappe/website/doctype/website_settings/website_settings.py`. In which, we find the `is_chat_enabled` function that has the `allow_guest=True` attribute

```python
@frappe.whitelist(allow_guest=True)
def is_chat_enabled():
	return bool(frappe.db.get_single_value('Website Settings', 'chat_enable'))
```