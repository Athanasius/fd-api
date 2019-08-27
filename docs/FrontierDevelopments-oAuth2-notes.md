# Introduction

  Since early 2019 Frontier Developments switched authorisation for their CAPI (Companion API)[0] service from plain username+password to an oAuth2 scheme.
  Before a developer can make any use of this they must first apply for access.

1. Navigate a web browser to <https://user.frontierstore.net/> and **apply** for access (I can't more fully document this because I long since went through the process and only have one applicable account).
2. Once Frontier have **approved** your access (it will _not_ be instant), navigate back to <https://user.frontierstore.net/> to review the available information.  You should default to the 'User Information' view which shows:

	1. Frontier ID - your unique ID for this system

	2. Name - The real name specified in your account

	3. Email - The email address associated with your account

	4. Platform - Whether this is a Frontier account, XBox, Playstation or Steam.  The 'Authorized Applications' lists all the applications you've authorised to request data on your behalf.  This might include sites like Inara.Cz.  

3. The 'Developer Zone' is where you'll see your authorised application
once access is granted.  You will probably have 'AUTH' and 'CAPI' scopes.
Clicking 'View' on this will reveal your Client ID and Shared Key.
You can also 'Regenerate key' here if you ever need to.

 There is also a link to <https://user.frontierstore.net/developer/docs>,
the developer documentation.  If you are wanting to use CAPI with a
standalone application, rather than a web-based application you will
need to follow the PKCE documentation.

 I found <https://www.oauth.com/oauth2-servers/pkce/> more useful
though.
  
[0] - It's called CAPI / Companion API because it was originally created
solely for the use of an authorised, third-party developed, Companion
application for iOS (an Android version was never produced).  Although
that application is long since dead (not working on many subsequent iOS
revisions), enough developers figured out the API and started making use
of it that Frontier Developments decided to continue supporting it.

## PKCE

  If your application does not run in a web browser than you'll want to
use PKCE for the authentication flow.  Example code here ends up using a
web browser for the Redirect URI anyway, but the principle is the same.

  If you have a good library available in your chosen development
environment then please feel free to use that.  If you're doing this all
"by hand", then read on.

### Authorization Request

  You'll want to craft an Authorization Request to pass to the user.
Either they'll have to copy and paste it into a browser, or perhaps
you can invoke a browser with it.

  This URL should be of the form:

	https://auth.frontierstore.net/auth?audience=frontier&scope=capi&response_type=code&client_id=YOUR_APPROVED_CLIENTID&code_challenge=CODE_CHALLENGE&code_challenge_method=S256&state=STATESTRING&redirect_uri=REDIRECT_URI

  An 'audience' of 'frontier' means a Frontier Developments account,
rather than a Steam, XBox, or Playstation account.
  A 'scope' of 'capi' means we're requesting access to the CAPI, instead
of just 'auth' which would just let us know some information associated
with the account (real name, email address).

  Obviously you need to replace the requisite parts of this:

1. YOUR_APPROVED_CLIENTID is your 'Client ID' from the Frontier
    'Developer Zone' for your application.
2. First we need to generate a CODE_VERIFIER.

	1. Generate 32 bytes (octets) of random data, as securely as you can.
	2. Base64 encode this, in a URL safe version; replace '+' with
      '-', and '/' with '_', but the '=' on the end needs to remain in
      place.

3. From this generate a CODE_CHALLENGE:

	1. Create a binary, not hex, representation of a sha256 hash of
      the raw, not string form, CODE_VERIFIER.
	2. Base64 encode this in a URL safe manner.  You **must**
     strip off the trailing '='.  If not you'll get:

			{"message":"An error occured.","logref":"<hex id>"}
     when you try to use this in the subsequent Token Request.

	3. Make sure you have a string representation of this (not, e.g.
      python bytes).

4. STATESTRING should be generated similarly to CODE_VERIFIER, and
    as with CODE_CHALLENGE ensure it's in a string representation.

5. REDIRECT_URI is how your app receives back the CODE from
    Frontier's auth servers.  If you do have a web server available then
    set up a receiving script there.  If operating on a mobile device
    you probably want to register a custom URL scheme handler and point to
    *that, e.g. myapp://fd-auth-redirect.  Just so long as:

	1. The web browser on the device understands and can reach this
       URL.
	2. You can then get the received CODE back into your application.

Now that you have crafted the Authorization Request URL, give it to the user.
They'll be asked to login on Frontier's server (if needs be) and then
approve your application's requested access.  The key thing is that with
PKCE you do **NOT** want to send a query to this URL yourself.

  Once the user has logged in and approved your Application you'll
receive a code back as a GET parameter at the REDIRECT_URI you
specified.

6. In the REDIRECT_URI handler you *should* check that the received STATE
matches what you originally sent in order to verify you're in sync with
the auth server.

### Token Request

7. Now craft a Token Request, which this time you *are* going to send
yourself.  Note you need to use a POST request, not GET.

	1. The URL is:

			https://auth.frontierstore.net/token

 	2. You need to set a header:

			Content-Type: application/x-www-form-urlencoded

	3. And the data in the body will be a string (NB: *not* a JSON
	   object!):

			redirect_uri=REDIRECT_URI&code=CODE&grant_type=authorization_code&code_verifier=CODE_VERIFIER&client_id=CLIENTID

		1. REDIRECT_URI - again a web script to receive the
		response.  You can re-use the same one if you're clever.
		This does need to be URL-Encoded (%XX versions of ':'
		and '/' at least).

		2. CODE - The value you received back as a 'code=XXX'
		GET parameter in the REDIRECT_URI script.

		3. CODE_VERIFIER - The URL-Safe Base64 version of your
		VERIFIER.  This **MUST** still have the trailing '=',
		else you'll get

			{"message":"An error occured.","logref":"<hex id>"}

		4. CLIENTID - Your Application's Client ID.

8. Send this Token Request and if it's all worked you'll get a 200 response,
with the body being a JSON object containing the tokens.  If you
did something wrong, or took too long, you'll likely get a 401
response.  
The JSON will contain a few keys and their values:
	1. access_token - the token to be used on CAPI endpoint requests

	2. refresh_token - the token that can be used to get a new
       access_token if the latter has expired, assuming this token hasn't
       also expired.

	3. token_type - "Bearer"

	4. expires_in - Seconds(?) until the (which?) token expires. 

### Summary

1. Generate a VERIFIER.  You'll then generate a CHALLENGE from this,
sent in the Authorization Request.  You will later send the
VERIFIER in the subsequent Token Request to prove it was you who made
the initial request.

2. Generate the initial Authorization Request, which will ask the user
to authorize your application's access to your account.

3. Success will cause the browser to go to the specified Redirect URI,
with a CODE and the STATUS you specified passed as GET parameters.

4. You then send a Token Request, including your VERIFIER, Client ID,
and the CODE you just got to ask for the Access and Refresh Tokens.
