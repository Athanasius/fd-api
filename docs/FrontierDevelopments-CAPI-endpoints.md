# Introduction
## oAuth2
See [FrontierDevelopments-oAuth2-notes](FrontierDevelopments-oAuth2-notes.md)
for how to use Frontier Developments' oAuth2 system for Authorization on
the CAPI.

In all instances you'll need to use the Access Token obtained via
oAuth2 by setting an HTTP header for the request:

        Authorization: Bearer <access_token>

Note that in theory the token type could be different from 'Bearer'.
It's safest to store the token_type that comes back from the request for
an Access Token and repeat that back in this header.

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
		GET <https://companion.orerve.net/profile>

provides access to the Cmdr's profile.  What follows is the last known
information about the output.  This will obviously be subject to change
as Frontier changes things.

	1. Where 'FDev ID' or 'FDev Symbol' is mentioned please see <https://github.com/EDCD/FDevIDs>

1. `commander`: Information about the Cmdr
	1. `name`: The Cmdr's Name
	1. `id`: Numerical ID
	1. `docked`: Whether currently docked
	1. `alive`: 
	1. `credits`: Credit Balance
	1. `debt`: Any current debt amount
	1. `currentShipId`: Numerical ID of current ship (index within
	   the Cmdr's currently owned ships, not necessarily unique over
	   time due to sell/buy).
	1. `rank`: Ranks
		1. `combat`
		1. `trade`
		1. `explore`
		1. `cqc`
		1. `empire`
		1. `federation`
		1. `power`
		1. `service`: ???
		1. `crime`
	1. `capabilities`: .e.g. whether the account has Horizons, and if it
	   can buy the Cobra Mk IV.
1. `shipName`: Current ship's Name
1. `id`: Current ship's Numerical ID (see `currentShipId` above)
1. Current Station, if applicable
	1. Name
	1. Numerical ID
1. `starsystem`: Current star system
1. `lastStarport`: Information about the last StarPort they were docked at
	1. `name`: Name
	1. `id`: Numerical ID
	1. `faction`: Allegiance to a Super Power, if any
	1. `minorfaction`: Minor Faction that owns this asset
	1. `services`: Available services
1. `lastSystem`: The last System they were in
	1. Name
	1. Allegiance ('faction')
	1. Numerical ID
1. `ship`: Current Ship data.  Note that this duplicates some data
   that's at the top level.
	1. `name`: Ship Name
	1. `shipID`: Ship ID
	1. Numerical ID
	1. `value` Ship Value, with breakdown cargo/modules/hull
		1. `hull`
		1. `modules`
		1. `cargo`
		1. `total`
		1. `unloaned`
	1. `alive`
	1. `oxygenRemaining`: Oxygen Remaining
	1. `modules`: The first key in each entry describes which slot
	   the module is for, and its size.
		1. `module`:
			1. `name`: FDev Symbol
			1. `id`: Numerical FDev ID
			1. `value`: Price bought for ('value')
			1. `locName`: Localised human readable name
			1. `locDescription`: Localised module
			   description.
			1. `priority`: Power Priority
			1. `on`: Powered Status (on/off)
			1. `free`: ??? Whether it came free with a ship?
			   It's 'false' on everything, even 'Planetary
			   Approach Suite' and the Fuel Tank.
			1. `health`: Current Health
		1. `engineer`: Details of currently applied engineering
			1. `recipeName`: Non-localised blueprint name
			1. `recipeLocName`: Localised blueprint name
			1. `recpieLocDescription`: Localised blueprint
			   description
			1. `recipeLevel`: Rank of the blueprint
			1. `engineerName`: Which engineer was used
			1. `engineerId`: Engineer's numerical ID
		1. `WorkInProgress_modifications`: Details about the
		   effects of the applied blueprint
		1. `specialModifications`: "Special Effects", empty
		   array if none
1. `launchBays`: Information about in-stock SRVs.  The top level key
   defines slot and size.
	1. `rebuilds`: How many spares???
	1. `name`: 'testbuggy' for an SRV
	1. `locName`: "SRV Scarab"
	1. `loadout`: "starter"
	1. `loadoutName`: "Starter" (Localised?)
1. Other Ships data
## Shipyard
## Market
## Journal

## HTTP Status Codes

1. 401 - Unauthorized - Since the 'September Update' patch on 2019-09-17
   the CAPI servers use this HTTP status code to signal that the
   provided Access Token is invalid (certainly for when it's expired).

   The body containing:

		{"status":401,"message":"JWT has incorrect\/unexpected fields"}
1. 418 - "I'm a teapot" - used to signal that the service is down for
   maintenance.  Technically Frontier shouldn't be using this as it's a
   joke from a couple of April Fools' RFCs:
   <https://tools.ietf.org/html/rfc2324>
   <https://tools.ietf.org/html/rfc7168>

1. 422 - "Unprocessable Entity" - previously used to signal that a provided
   Access Token was invalid, likely due to it being expired.  This changed with
   the 'September Update' patch in 2019.
