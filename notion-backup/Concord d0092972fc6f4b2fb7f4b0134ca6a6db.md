# Concord

*Authentication bypass and RCE*

Workflow servers automate the development workflow, execute necessary build and deployment commands and call various APIs. However, these workflow servers must be granted access to code in Dev, QA and Prod environments and hence are prime attack targets.

Concord workflow server suffers from 3 different authentication bypass vulnerabilities: 

- Permissive CORS header information disclosure vulnerability
- Cross-site Request Forgery vulnerability
- Default user accounts that can be accessed with undocumented API keys

## Credentials

Application URL: [http://concord:8001](http://concord:8001)

| Login | USERNAME | PASSWORD |
| --- | --- | --- |
| SSH | student | studentlab |

[Discovery](Concord%20d0092972fc6f4b2fb7f4b0134ca6a6db/Discovery%2032137e28789d46ed88148b3a19ce903c.md)

[Authentication Bypass: CSRF and CORS](Concord%20d0092972fc6f4b2fb7f4b0134ca6a6db/Authentication%20Bypass%20CSRF%20and%20CORS%20658a554abaa9455a8e07bb61d46f2080.md)

[Extra Mile 11.2.5.2](Concord%20d0092972fc6f4b2fb7f4b0134ca6a6db/Extra%20Mile%2011%202%205%202%204f92377a39d24b81b765c7d434fe23a4.md)

[Authentication Bypass: Insecure Defaults](Concord%20d0092972fc6f4b2fb7f4b0134ca6a6db/Authentication%20Bypass%20Insecure%20Defaults%20406759fa1a0c4fda881fb7028d72cf73.md)