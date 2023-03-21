**This project is no longer maintained.  Please feel free to fork and continue it if you have the need.**
===

Tue 21 Mar 10:40:34 GMT 2023
===
  It has come to light that whilst Frontier's Auth service will happily
give you an Access and Refresh Token if you only ask for `scope=capi`
(rather than `scope=auth capi`), the Access Token now does not contain
some fields.
  This would be fine ... except the CAPI service is objecting to it:

    HTTP Status 401 - Access Token expired: {"status":401,"message":"Authentication token incomplete","missing":["email","firstname","lastname"],"tag":"<elided>"}

Thus, for the time being, *this* code will not work unless you edit
`oauth2-pkce.py:148` so it uses `scope=auth capi`.

---


*This is a work in progress.  The master branch now has working code,
but for the latest check if the fdev-oauth2 branch is ahead.*

See [documentation](docs/README.md) for details on how this all works,
including a walk-through for how to handle the oAuth2 flow yourself.

See [TODO](docs/TODO.md) for what is/isn't implemented.

The main script is 'fd-ed-capi.py' so run:

                fd-ed-capi.py --help
to check the options.

---

This project is written in Python 3.x (tested on 3.7.x) and implements
the oAuth2 Authorization mechanism before allowing you to retrieve data
from the Companion API (CAPI) end points.
