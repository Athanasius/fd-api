**This is now obsolete, as Frontier Developments moved over to an OAuth2
based authentication scheme.**

I've started some work in the "fdev-oauth2" branch to get PKCE
authentication working.  This time in Python3 rather than Perl.

---

Code for retrieving an Elite Dangerous Commander's profile data using
the iOS App API.

See docs/ directory for details on how it works.

To use this code you'll need to put at least your username/email and
password into config.txt:

```
user_name: someuser@example.com
user_password: YourSuperSecretPassword
```

At time of typing the code just spits out the resulting profile data.
It's retrieved as a JSON object so easy enough to work with.
