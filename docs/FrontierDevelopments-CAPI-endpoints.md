# Introduction
## oAuth2
See [FrontierDevelopments-oAuth2-notes](FrontierDevelopments-oAuth2-notes.md)
for how to use Frontier Developments' oAuth2 system for Authorization on
the CAPI.

---
You might occasionally see a header:

		Set-Cookie: access_token=1566841911%7C%7C<40 character hex string>; domain=companion.orerve.net; path=/; expires=Mon, 26-Aug-2019 17:51:51 UTC; secure
in the responses from the CAPI end points.  This seems to serve no
purpose, and is perhaps left over from the work to implement oAuth2 on
the service.

1. The start of the access_token value appears to be a Unix
Epoch timestamp, 86400 seconds in the past.  That matches the
expiry time on the cookie.
2. That "40 character hex string" doesn't seem to be a valid
JSON Web Token, for instance, or otherwise related to either
the Refresh or Access Tokens.
## Profile
## Shipyard
## Market
## Journal

## HTTP Status Codes

1. 418 - "I'm a teapot" - used to signal that the service is down for
   maintenance.
