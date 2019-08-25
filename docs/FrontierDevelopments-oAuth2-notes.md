Introduction
============

  Since early 2019 Frontier Developments switched authorisation for their CAPI (Companion API)[0] service from plain username+password to an oAuth2 scheme.
  Before a developer can make any use of this they must first apply for access.

1. Navigate a web browser to <https://user.frontierstore.net/> and *apply* for access (I can't more fully document this because I long since went through the process and only have one applicable account).
2. Once Frontier have *approved* your access (it will _not_ be instant), navigate back to <https://user.frontierstore.net/> to review the available information.  You should default to the 'User Information' view which shows: a. Frontier ID - your unique ID for this system
	1. Name - The real name specified in your account
	2. Email - The email address associated with your account
	3. Platform - Whether this is a Frontier account, XBox, Playstation or Steam.  The 'Authorized Applications' lists all the applications you've authorised to request data on your behalf.  This might include sites like Inara.Cz.  
3. The 'Developer Zone' is where you'll see your authorised application once access is granted.  You will probably have 'AUTH' and 'CAPI' scopes.  Clicking 'View' on this will reveal your Client ID and Shared Key.  You can also 'Regenerate key' here if you ever need to.  

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

PKCE
----

  If your application does not run in a web browser than you'll want to
use PKCE for the authentication flow.

  If you have a good library available in your chosen development
environment then please feel free to use that.  If you're doing this all
"by hand", then read on.

  You'll want to craft a URL to pass to the user.  Either they'll have
to copy and paste it into a browser, or perhaps you can invoke a browser
with it.
  This URL should be of the form:

<https://auth.frontierstore.net/auth?audience=frontier&scope=capi&response_type=code&client_id=YOUR_APPROVED_CLIENTID&code_challenge=CODE_CHALLENGE&code_challenge_method=S256&state=STATESTRING&redirect_uri=REDIRECT_URI>

  Obviously you need to replace the requisite parts of this:

1. YOUR_APPROVED_CLIENTID is your 'ClientID' from the Frontier
    'Developer Zone' for your application.
2. CODE_CHALLENGE needs to be generated from a CODE_VERIFIER.

	1. Generate 32 bytes (octets) of random data, as securely as you can.
	2. Now Base64 encode this, in a URL safe version (replace '+' with
      '-', and '/' with '_', but the '=' on the end can stay).

2. This is your CODE_VERIFIER.  Now we generate the CODE_CHALLENGE:

	1. Create a, binary not hex representation, sha256 hash of
      CODE_VERIFIER.
	2. Again, Base64 encode this in a URL safe manner.  You WILL need
     to strip the trailing '=' off it this time.
	3. Make sure you have a string representation of this (not, e.g.
      python bytes).

3. STATESTRING should be generated similarly to CODE_VERIFIER, and
    as with CODE_CHALLENGE ensure it's in a string representation.
4. REDIRECT_URI is how your app receives back the CODE from
    Frontier's auth servers.  If you do have a web server available then
    set up a receiving script there.  If operating on a mobile device
    you probably want to register a custom URL handler and point to
    that.  Just so long as:

	1. The web browser on the device understands and can reach this
       URL.
	2. You can then get the received CODE back into your application.

Also note that I chose an 'audience' of 'frontier' (PC non-steam
account), and a scope of 'capi' (in order to use the CAPI).

Now that you have crafted the initial URL, give it to the user.
They'll be asked to login on Frontier's server (if needs be) and then
approve your application's requested access.  The key thing is that with
PKCE you do *NOT* want to send a query to this URL yourself.

  Once the user has logged in and approved your Application you'll
receive a code back as a GET parameter at the REDIRECT_URI you
specified.

5. In the REDIRECT_URL handler check the received STATE matches what
    you originally sent in order to verify you're in sync with the auth
    server.

6. Now you need to craft a new https request, which this time you *are*
    going to use yourself.  Note you need to use a POST request, not
    GET.

 <https://auth.frontierstore.net/token>

 You need to set a header:

  Content-Type: application/x-www-form-urlencoded

 And the data in the body will be a string:

  redirect_uri=REDIRECT_URI&code=CODE&grant_type=authorization_code&code_verifier=CODE_VERIFIER&client_id=CLIENTID

	1. REDIRECT_URI - again a web script to receive the response.  You
       can re-use the same one if you're clever.  This does need to be
       URL-Encoded (%XX versions of ':' and '/' at least).

	2. CODE - The value you received back as a 'code=XXX' GET
       parameter in the REDIRECT_URI script.

	3. CODE_VERIFIER - The URL-Safe Base64 version of your VERIFIER,
       *with* the trailing '='.

	4. CLIENTID - Your Application's CLIENTID.

    Make this request and if it's all worked you'll get a 200 response,
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
