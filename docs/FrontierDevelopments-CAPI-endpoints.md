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
		NB: This has been observed to sometimes be the
		id64/SystemAddress of the system, and other times be
		some other id.  The `ship` section below then contains
		`id` matching this *and* `systemaddress` with the id64.
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

---

## Shipyard

    	GET <https://companion.orerve.net/shipyard>

Fetches the last visited shipyard for the authenticated commander.

CommodityId, EconomyId, ShipId can be found in the [EDCD/FDevIDs repo](https://github.com/EDCD/FDevIDs)

1. `id` - Station ID
1. `name` - Station name
1. `outpostType` - What type of outpost it is, examples: `starport`, `fleetcarrier`
1. `imported` - What commodities that are imported from this station (dictionary, commodity id and key)
   - Example `"128049162": "Cobalt"`
1. `exported` - What commodities that are exported from this station (dictionary, commodity id and key)
   - Example `"128049162": "Cobalt"`
1. `services` - What services the station provides and their status
	1. `dock` - Status of Dock (`ok`, `unavailable`, `private`)
	1. `contacts` - Status of Contacts (`ok`, `unavailable`, `private`)
	1. `exploration` - Status of Exploration (`ok`, `unavailable`, `private`)
	1. `commodities` - Status of Commodities (`ok`, `unavailable`, `private`)
	1. `refuel` - Status of Refuel (`ok`, `unavailable`, `private`)
	1. `repair` - Status of Repair (`ok`, `unavailable`, `private`)
	1. `rearm` - Status of Rearm (`ok`, `unavailable`, `private`)
	1. `outfitting` - Status of Outfitting (`ok`, `unavailable`, `private`)
	1. `shipyard` - Status of Shipyard (`ok`, `unavailable`, `private`)
	1. `crewlounge` - Status of Crewlounge (`ok`, `unavailable`, `private`)
	1. `searchrescue` - Status of Search & Rescue (`ok`, `unavailable`, `private`)
	1. `techbroker` - Status of Tech broker (`ok`, `unavailable`, `private`)
	1. `stationmenu` - Status of Station menu (`ok`, `unavailable`, `private`)
	1. `shop` - Status of shop (`ok`, `unavailable`, `private`)
	1. `engineer` - Status of engineers (`ok`, `unavailable`, `private`)
1. `economies` - What different types of economies you can expect from the station (dictionary, economyId as key)
	- Example `"23": { "name" : "HighTech", "proportion": 0.7 }`
1. `prohibited` - What commidities that are prohibited on this station (dictionary, commodityId and key)
   - Example `"128049162": "Cobalt"`
1. `modules` - The list of modules on this station (dictionary, moduleId as key)
	1. `id` - ModuleId
	1. `category` - What category this module is
	1. `name` - Name for the module
	1. `cost` - Module cost
	1. `sku` - The SKU for the module
	1. `stock` - How many are available of this item, `-1` means unlimited
1. `ships` - The list of available ships on this station
	1. `shipyard_list` - The actual list (Dictionary, ship name as key)
		1. `id` - ShipId
		1. `name` - Ship name
		1. `basevalue` - The base cost of a new ship
		1. `sku` - The SKU for the ship
		1. `stock` - How many of this ship we have in stock

---

## Fleetcarrier

    	GET <https://companion.orerve.net/fleetcarrier>

Fetches the fleet carrier data, that the authenticated commander owns

CommodityId, EconomyId, ShipId can be found in the [EDCD/FDevIDs repo](https://github.com/EDCD/FDevIDs)

1. `name` - The name for the carrier
	1. `callsign` - The callsign of the fleet carrier
	1. `vanityName`
	1. `filteredVanityName`
1. `currentStarSystem` - The current location of the carrier
1. `balance` - The current balance (credits) on this carrier
1. `fuel` - How much fuel this carrier has (Tritium)
1. `state` - 
1. `theme` - What type of carrier we're dealing with (UI theme)
1. `dockingAccess` - Declare who can dock with this carrier
1. `notoriousAccess` - 
1. `capacity` - The capacity status of the different things available
	1. `shipPacks`
	1. `modulePacks`
	1. `cargoForSale`
	1. `cargoNotForSale`
	1. `cargoSpaceReserved`
	1. `crew`
	1. `freeSpace`
1. `itinerary`
	1. `completed` - History data over completed jumps with the carrier
		1. `departureTime` - When the carrier left the system
		1. `arrivalTime` - When the carrier arrived to the system
		1. `state` - Was the jump successful, cancelled or any other state?
		1. `visitDurationSeconds` - How many seconds were spent in the system
		1. `starsystem` - The visited starsystem
	1. `totalDistanceJumpedLY` - How many lightyears this carrier has ever jumped
	1. `currentJump` - The currently scheduled jump, can be null
1. `marketFinance`
	1. `cargoTotalValue` - The total value (credits) of the cargo
	1. `allTimeProfit` - How much profit this carrier has made, all time
	1. `numCommodsForSale` - How many commodities are for sale
	1. `numCommodsPurchaseOrders` - How many purchase orders for commodities there are
	1. `balanceAllocForPurchaseOrders` - How many credits are allocated for purchase orders
1. `blackmarketFinance`
	1. `cargoTotalValue` - The total value (credits) of the cargo
	1. `allTimeProfit` - How much profit this carrier has made, all time
	1. `numCommodsForSale` - How many commodities are for sale
	1. `numCommodsPurchaseOrders` - How many purchase orders for commodities there are
	1. `balanceAllocForPurchaseOrders` - How many credits are allocated for purchase orders
1. `finance`
	1. `bankBalance` - How much credits are in the bank of the carrier
	1. `bankReservedBalance` - How much of said credits are reserved
	1. `taxation` - The taxation on sales/purchases
	1. `numServices` - How many services are active
	1. `numOptionalServices` - How many optional services are active
	1. `debtThreshold` - Declares the debt threshold
	1. `maintenance` - How much maintenance costs
	1. `maintenanceToDate` - How much maintenance has been paid to date
	1. `coreCost` - Core costs for the carrier
	1. `servicesCost` - The costs for services
	1. `servicesCostToDate` - How much services costs has been paid to date
	1. `jumpsCost` - How much a jump costs
	1. `numJumps` - Number of jumps
1. `servicesCrew`
1. `cargo`
	1. `commodity` - The commodity available
	1. `mission` - Is this a mission commodity?
	1. `qty` - The quantity available of this commodity
	1. `value` - The value (credits) of this commodity
	1. `stolen` - Was this item stolen?
	1. `locName` - Localised name of the commodity
1. `reputation`
	- Reputation is an array with objects that describe ties to the major factions
	1. `majorFaction` - The major faction
	1. `score` - The reputation score
1. `market`
	- Contains the same information as a call to [`/market`](#market), check that for more info
1. `ships`
	- Contains the same information as the modules in [`/shipyard`](#shipyard), check that for more info
1. `modules`
	- Contains the same information as the modules in [`/shipyard`](#shipyard), check that for more info

---

## Market

    	GET <https://companion.orerve.net/market>

Get the market data from the last docked station/fleet carrier/settlement and contains their services and status, what type of economics it has, what they import, export and what is forbidden. (And also the commodities, with price info and stock/demand)

CommodityId can be found in the [EDCD/FDevIDs repo](https://github.com/EDCD/FDevIDs)

1. `id` - Station ID
1. `name` - Station name
1. `outpostType` - What type of outpost it is, examples: `starport`, `fleetcarrier`
1. `imported` - What commodities that are imported from this station (dictionary, commodity id and key)
   - Example `"128049162": "Cobalt"`
1. `exported` - What commodities that are exported from this station (dictionary, commodity id and key)
   - Example `"128049162": "Cobalt"`
1. `services` - What services the station provides and their status
	1. `dock` - Status of Dock (`ok`, `unavailable`, `private`)
	1. `contacts` - Status of Contacts (`ok`, `unavailable`, `private`)
	1. `exploration` - Status of Exploration (`ok`, `unavailable`, `private`)
	1. `commodities` - Status of Commodities (`ok`, `unavailable`, `private`)
	1. `refuel` - Status of Refuel (`ok`, `unavailable`, `private`)
	1. `repair` - Status of Repair (`ok`, `unavailable`, `private`)
	1. `rearm` - Status of Rearm (`ok`, `unavailable`, `private`)
	1. `outfitting` - Status of Outfitting (`ok`, `unavailable`, `private`)
	1. `shipyard` - Status of Shipyard (`ok`, `unavailable`, `private`)
	1. `crewlounge` - Status of Crewlounge (`ok`, `unavailable`, `private`)
	1. `searchrescue` - Status of Search & Rescue (`ok`, `unavailable`, `private`)
	1. `techbroker` - Status of Tech broker (`ok`, `unavailable`, `private`)
	1. `stationmenu` - Status of Station menu (`ok`, `unavailable`, `private`)
	1. `shop` - Status of shop (`ok`, `unavailable`, `private`)
	1. `engineer` - Status of engineers (`ok`, `unavailable`, `private`)
1. `economies` - What different types of economies you can expect from the station (dictionary, economyId as key)
	- Example `"23": { "name" : "HighTech", "proportion": 0.7 }`
1. `prohibited` - What commidities that are prohibited on this station (dictionary, commodityId as key)
   - Example `"128049162": "Cobalt"`
1. `commodities` - All available commodities and their info
	1. `id` - Commodity ID
	1. `name` - Commodity name
	1. `legality` - Status of the legality of this commodity at this station, empty string = legal
	1. `buyPrice` - The buy price at the moment of the visit
	1. `sellPrice` - The sell price at the moment of the visit
	1. `meanPrice` - The mean price at the momenf of the visit
	1. `demandBracket` - How much in demand this commodity is, value between `0` and `3`
	1. `stockBracket` - How much in stock this commodity has (bracket), value between `0` and `3`
	1. `stock` - How many items are in stock of this commodity
	1. `demand` - How many items the station has demand for (more is better)
	1. `statusFlags`
	1. `categoryName` - What type of category the commodity belongs to
	1. `locName` - Localised name

---

## Journal

Gives access to the authenticated players journals, all sessions are combined into a single file for a single request

### Request endpoints

-   `GET <https://companion.orerve.net/journal>`
-   `GET <https://companion.orerve.net/journal/[year (4 numbers)]/[month (2 numbers)]/[day (2 numbers)]>`

Example requests:

```plain
GET <https://companion.oreve.net/journal>
```

This request give you the current day journal data

```plain
GET <https://companion.oreve.net/journal/2020/12/30>
```

This request would give you the journal for the specific date, in this case the 30th December, 2020.

### Response codes

| Code  | Status          | Description                                                                                          |
| :---- | :-------------- | :--------------------------------------------------------------------------------------------------- |
| `200` | OK              | This means you got the entire journal for the specified request                                      |
| `204` | No Content | This means that the player has not (yet) played this day |
| `206` | Partial Content | The request did not get the entire journal, best solution is to keep trying until you get `200 - OK` |
| `401` | Unauthorized    | See [HTTP Status Codes](#http-status-codes) for more information                                     |

### Expected output

To know what kind of output you can except from the `/journal` endpoint, we recommend reading the [Journal Manual](https://hosting.zaonce.net/community/journal/v28/Journal_Manual_v28.pdf) to see what you can encounter.

---

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
