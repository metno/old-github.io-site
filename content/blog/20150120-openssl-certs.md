Title: OpenSSL commands to handle certificates
Date: 2015-01-20
Tags: tips, openssl
Slug: openssl-certs
Author: arnulf.heimsbakk@met.no
Status: draft

openssl x509 -noout -dates -in example.crt

notBefore=Jan 20 09:52:11 2015 GMT
notAfter=Jan 19 09:52:11 2018 GMT


penssl rsa -noout -modulus -in example.key

openssl x509 -noout -modulus -in example.crt


###### vim: set syn=markdown spell spl=en:

