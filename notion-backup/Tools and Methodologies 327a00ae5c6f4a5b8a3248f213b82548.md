# Tools and Methodologies

# Python Web Listeners

```python
import requests
from colorma import Fore, Back, Style

requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
def format_text(title,item):
   cr = '\r\n'
   section_break = cr +  "*" * 20 + cr
   item = str(item)
   text = Style.BRIGHT + Fore.RED + title + Fore.RESET + section_break + item + section_break
   return text

r = requests.get('https://manageengine:8443/',verify=False)
print(format_text('r.status_code is: ',r.status_code))
print(format_text('r.headers is: ',r.headers))
print(format_text('r.cookies is: ',r.cookies))
print(format_text('r.text is: ',r.text))
```

To enable the use of proxies, use:

```python
proxies = {'http':'http://127.0.0.1:8080','https':'http://127.0.0.1:8080'}
r = requests.get('https://manageengine:8443/',verify=False,proxies=proxies)
```

# Source Code Recovery

Recover source code from web applications written in compiled languages, particularly for JAVA and .NET source code recovery. 

## File Transfer

We can sometimes transfer the source code from our client to Kali. 

```bash
rsync -azP <user>@<ip>:/home/<path> ./
scp -r <user>@<ip>:/home/path .
```

## .NET

Compilation into exe (save file as `sc.exe`)

```python
csc.exe test.cs
```

Open dnSpy and decompile the executable’s code by dragging test.exe file to dnSpy window to trigger decomplication process.

### Cross References

Decompilers can find cross-references to particular variable or function to better understand code logic. 

- Can search for specific variables (i.e. searching for variables with base64 when dealing with base64 values inside requests)
- Select Analyze from context menu of function

### Modifying Assemblies

- Can use edit class (C3) in program to edit executable file with dnSpy to insert debugging statements to log files to better debug application.
- Compile, then File > Save All to overwrite original version of executable

## Java

Decompile with JD-GUI decompiler. Java-based web applications primarily consist of compiled Java class files compressed into single file, Java archive (JAR) file. 

Compile JAR file:

```bash
javac -source 1.8 -target 1.8 test.java

Create manifest file:
mkdir META-INF
echo "Main-Class: test" > META-INF/MANIFEST.MF

Create JAR file:
jar cmvf META-INF/MANIFEST.MF test.jar test.class

Run jar file:
java -jar test.jar
```

Open JAR file in JD-GUI

# Source Code Analysis

Should understand software stack and intended use cases. Spend time walking through web application in browser and proxies to familiarize with functionality before source code analysis.  

- Can either search for specific vulnerable functionality (i.e. specific SQL query syntax) or go from the front-end perspective and look for HTTP request handlers.
- Data enters applications through source (i.e. POST request) and ends up in a sink (i.e. database)
- When we find vulnerable function, can search for references and where the function is used (right click on function and select Find All References)
- Searching for regex patterns with grep

```bash
grep -rnw -e "function search.*" <directory> --color
```

- When vim is unavailable, can use nano

```bash
Enable nano within tmux:
export TERM=xterm

Important shortcuts
Ctrl + W: Search
Ctrl + O: Save
Ctrl + X: Exit
Use nano -c [filename] to view line/col number
```

- If the source code implements some form of Regex, we can try matching it against sample strings to design our own payloads. We can test them out here: [regex101: build, test, and debug regex](https://regex101.com/)

## HTTP Routing Patterns

HTTP routing dictates how applications receive HTTP request and determines what code to run to generate associated response.

- File System Routing maps file URL to file on server’s filesystem. Web servers define a document root, where it stores externally accessible files.
- Servlet Mappings are used by some Java web applications, where a `web.xml` file stores HTTP routing configurations. Each route is made up of 2 entries, 1 to define servlet and second to map URL to servlet.
- Some programming languages include routing information directly in source code (Flask, ExpressJS)
    - Routing by annotation/attribute (Spring MVC and Flask) where annotation is declared next to method or function handling HTTP request

## High Priority Targets

- Check unauthenticated areas
- Check authenticated portions (that are likely to receive less attention)
- Investigate sanitation of user input (trusted library or custom solution)
- Database (query construction, parametrization of input)
- Inspect logic for account creation and password reset and recovery (try to subvert functionality)
- Operating system interactions (modify or inject commands)
- Programming language specific vulnerabilities

# Debugging

Running application through a debugger allows for inspection of application memory and call stacks. 

- Install RedHat Language support for Java and Microsoft Debugger for Java
- Set a breakpoint by clicking to the left of line numbers (for red dot to appear)
- Step Over allows next method call to execute and pause execution at next line in current method
- Step Into follows execution flow and pause
- Step Out would complete current method call and pause

Some debuggers support debugging process running on remote system. 

- Requires access to source code and debugger port on remote system

[PHP](Tools%20and%20Methodologies%20327a00ae5c6f4a5b8a3248f213b82548/PHP%20df6088fab84f466492e14c76d6751576.md)

[SQL Commands](Tools%20and%20Methodologies%20327a00ae5c6f4a5b8a3248f213b82548/SQL%20Commands%20446f9e0860f843d9a216a305d1d4f00d.md)

[Searching for Entry Points](Tools%20and%20Methodologies%20327a00ae5c6f4a5b8a3248f213b82548/Searching%20for%20Entry%20Points%2016da982c8a864855bcc1b0383ec72a2d.md)