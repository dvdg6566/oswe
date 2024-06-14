# openITCOCKPIT

XSS and OS Command Injection

Application that aids in the configuration and management of 2 popular monitoring utilities: Nagios and Naemon. 

## Credentials

Remember to set hosts file with openCRX IP address

| Login | USERNAME | PASSWORD |
| --- | --- | --- |
| SSH | student | studentlab |
| Application | view@viewer.local | 27NZDLgfnY |

## Blackbox Testing

Discern when to continue investigating particular features and when to move on.

- SQL Syntax error obviously suggests presence of SQL injection vulnerability. However, unlike in white box testing, we can’t just reference the code and check for proper escaping. This is significantly harder in a blackbox.

Discovery phase is critical to build a proper sitemap to obtain a view of exposed endpoints and application libraries. 

[Application Discovery](openITCOCKPIT%201f9b6d31769c43078b8a4aa3b99ec069/Application%20Discovery%20d16be10559d14582abe953b8684973fa.md)

[DOM-based XSS](openITCOCKPIT%201f9b6d31769c43078b8a4aa3b99ec069/DOM-based%20XSS%2093f096fc920441d28a4c34cb897b2b71.md)

[WebSocket RCE](openITCOCKPIT%201f9b6d31769c43078b8a4aa3b99ec069/WebSocket%20RCE%209355aa919b854eefafe37a538fe64323.md)

[10.7.6.2 Extra Mile](openITCOCKPIT%201f9b6d31769c43078b8a4aa3b99ec069/10%207%206%202%20Extra%20Mile%209a0be88a3c1c4f43adde9fd06cfebc2f.md)