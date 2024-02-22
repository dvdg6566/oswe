# ATutor LMS Type Juggling

## Summary

- PHP Type Juggling vulnerability in ATutor

## Setup

ATutor VM needs to send emails, we are using Atmail VM as SMTP relay. Configure Postfix on the ATutor VM with the correct IP address of the Atmail VM through the `/etc/postfix/transport` configuration file. 

```bash
offsec.local	smtp:[192.168.121.106]:587

sudo postmap /etc/postfix/transport
sudo systemctl restart postfix.service
```

This allows ATutor VM to send emails to Atmail VM as a relay server. 

[PHP Comparisons](ATutor%20LMS%20Type%20Juggling%201181c74fa6c44a3095e135432e476061/PHP%20Comparisons%2066d68595ee6644b7a2cd8a94e9334541.md)

[Vulnerability Discovery](ATutor%20LMS%20Type%20Juggling%201181c74fa6c44a3095e135432e476061/Vulnerability%20Discovery%20c3f8408782514894bf667f27ef17eee1.md)

[ATmail Server](ATutor%20LMS%20Type%20Juggling%201181c74fa6c44a3095e135432e476061/ATmail%20Server%2042ab9ba8523c4baa94b360c621bbef2d.md)

[Extra Mile](ATutor%20LMS%20Type%20Juggling%201181c74fa6c44a3095e135432e476061/Extra%20Mile%2062850c24a61a4108ac4fb612e6944e4b.md)