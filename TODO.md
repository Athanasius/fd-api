1. Figure out a way to have a single request.Session so that we can set
a User-Agent of the form:

		EDCD-[A-Za-z]+-[.0-9]+
    without having to remember it on every request.

1. Implement use of Access Token against all available endpoints.
	1. CAPI profile - DONE
	1. CAPI market
	1. CAPI shipyard
	1. CAPI journal
		1. CAPI journal current
		1. CAPI journal historic
1. Find out what the expiry time is on a Refresh Token, and what exactly
   happens if you try to use it.
1. Implement automatically firing the whole Authorization mechanism if
   both Access Token and Refresh Token are expired.  This may well
   entail first merging the oauth2-pkce.py script into the
   org.miggy.edcapi namespace.
1. Implement non-PKCE authorization flow and document it.
