1. Figure out a way to have a single request.Session so that we can set
a User-Agent of the form:

		EDCD-[A-Za-z]+-[.0-9]+
    without having to remember it on every request.

1. Implement use of Access Token against all available endpoints.
	1. CAPI profile
	1. CAPI market
	1. CAPI shipyard
	1. CAPI journal
		1. CAPI journal current
		1. CAPI journal historic
1. Implement use of Refresh Token as needed.

		curl -v -d 'grant_type=refresh_token&client_id=CLIENTID&client_secret=SECRETKEY&refresh_token=REFRESH_TOKEN' -H 'Content-Type: application/x-www-form-urlencoded' 'https://auth.frontierstore.net/token'
	1. Also ensure storing latest Refresh Token (is it a new one on
	   each API access?).
1. Implement non-PKCE authorization flow and document it.
