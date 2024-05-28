# Searching for Entry Points

1. We can look for any **entry points** or handlers to HTTP requests. For each of these, we’re going backwards through the code, and trying to look for any potentially dangerous handling of our requests (i.e. through SQL or deserialization)

```java
PHP:
grep -rnw /var/www/html/ATutor -e "^.*user_location.*public.*" --color

Java Servlets:
Search for doGet and doPost functions

.NET:
Look for anything that handles the HTTP request (httpContext.request.cookies or request.getParameter)

Python:
Check the specific framework, but many frameworks have some distinctive statement for routing functions ((i.e. @frappe.whitelist or @app.route for Flask)
```

1. Searching for SQL statements: We can search for SQL statements in the code. to look for potential SQL injection vulnerabilities. When investigating them, we are looking for ways to traceback our variables all the way to something user-controlled, especially if it comes in as unsansitized input from a HTTP request. 

```java
^.*?query.*?select.*?
^.*?query.*?SELECT.*?WHERE.*?\+.*?
```

1. Look for some kind of code injection surface, where there are functions that may execute and/or interpret our user-input. 

```java
Java:
Search for the eval() statement
```