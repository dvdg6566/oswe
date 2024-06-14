# 10.7.6.2 Extra Mile

*Find a readable database configuration and read the password. The user we exploited in the XSS
was not an administrator of the application. Use the database password to elevate privileges of
the “viewer” user to the administrator and reset the password to allow you to login. The
openITCOCKPIT application allows administrative users to create custom commands. Using this
feature and an administrator’s account, find and “exploit” this feature*

## Setup

From the mySQL database, we can set the `usergroup` to be equal to 1 (administrators) for the viewer user.  

```sql
UPDATE users SET usergroup_id = 1 WHERE id=2;

select * from openitcockpit.users;

UPDATE openitcockpit.users
SET password = "b7b56fad3c414b8e2dcb461c9c31fdaf7d78a1e3"
WHERE id = 1;
```

## Vulnerability Discovery

We can open the administrator and non-administrator accounts and compare them to look for additional functionality on the administrator account. 

```
**Configuration**
ConfigurationFiles (Seem to allow for updating of configuration files)
Grafana

**Administration**
Debugging (provides phpinfo debugging page)
Web root: /usr/share/openitcockpit/app/webroot
Anonymous Statistics

```

We can create a new command. How to trigger the command?