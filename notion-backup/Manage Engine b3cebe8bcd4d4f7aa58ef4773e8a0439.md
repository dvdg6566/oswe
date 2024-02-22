# Manage Engine

*ManageEngine Applications Manager is an application performance monitoring solution that proactively monitors business applications and help businesses ensure their revenue-critical applications meet end user expectations. Applications Manager offers out of the box monitoring support for 80+ applications and servers.*

- Audit compiled Java Servlets to detect critical vulnerabilities.

## Login Credentials

| Login | USERNAME | PASSWORD |
| --- | --- | --- |
| https://manageengine:8443/ | admin | admin |
| OS | Administrator | studentlab |
| PostgreSQL | postgres | appmanager |

RDP Command: `xfreerdp /v:192.168.206.113 /u:administrator /p:studentlab /tls-seclevel:0 /size:90%h` 

- For poor RDP performance: `sudo ifconfig tun0 mtu 1250`

## Setup

### Database Logging

To enable logging on PostgreSQL database, we edit its configuration file found atm `.\pgsql\data\amdb\postgresql.conf` .

```java
log_statement = 'all'			# none, ddl, mod, all
Remember to remove the # in front of the statement. 
```

We then launch the `services.msc`and find the ManageEngine Application Service. 

Logs will be available at the directory `.\pgsql\data\amdb\pgsql_log\`. 

We can also use the `pgAdmin` application, a front-end for postgreSQL. Alternatively, can use `psql.exe` to interact with application on port 15432. 

```java
psql.exe -U postgres -p 15432
```

## Reconnaissance

Looking around the application, we find that most URIs contain the `.do` extension, which is typically a URL mapping scheme for compiled Java applications. 

Can use process explorer to gain insight into the Java process that we are targeting. 

- If there are multiple Java processes, we can check any process by right clicking on the process and choosing properties to see the application path.
- In this case, our process uses an active working directory of `C:\Program Files (x86)\ManageEngine\AppManager12\working\`.

Within the working directory, we can find a deployment descriptor file `web.xml`, which is usually found in the default configuration folder `WEB-INF`. 

Inside the `WEB-INF\lib` directory, most of them are standard third-party `.jar` library names, apart from 4 of them. Jar files contain compiled Java classes and can be de-compiled into original Java source code using the JD-GUI decompiler. 

- We can use `File > Save All Sources` to export our decompiled to a file to open in more user-friendly applications like Notepad++.
- We can look at `AdventNetAppManagerWebClient.jar` since it likely contains information pertaining to our web app.

[SQL Injection](Manage%20Engine%20b3cebe8bcd4d4f7aa58ef4773e8a0439/SQL%20Injection%20b3fe3149924f47868408c9df499528cf.md)

[Reverse Shell 1: VBS](Manage%20Engine%20b3cebe8bcd4d4f7aa58ef4773e8a0439/Reverse%20Shell%201%20VBS%20527a784124e947f7a6f27f1946597f26.md)

[Reverse Shell 2: JSP Shell](Manage%20Engine%20b3cebe8bcd4d4f7aa58ef4773e8a0439/Reverse%20Shell%202%20JSP%20Shell%20e893780e5a75429db3c4cbd7d21ef546.md)

[Reverse Shell 3: Postgres UDF](Manage%20Engine%20b3cebe8bcd4d4f7aa58ef4773e8a0439/Reverse%20Shell%203%20Postgres%20UDF%20c2144c4c369b486f9618636e50ecfd39.md)

[Reverse Shell 3b: Postgres Large Objects](Manage%20Engine%20b3cebe8bcd4d4f7aa58ef4773e8a0439/Reverse%20Shell%203b%20Postgres%20Large%20Objects%20b1bc2235bedf414eb3ebb233d3429f0f.md)

[Extra Mile 5.8.2](Manage%20Engine%20b3cebe8bcd4d4f7aa58ef4773e8a0439/Extra%20Mile%205%208%202%20a678e82bddf74d2698efc5b9263911ba.md)