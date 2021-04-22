#!/usr/bin/env python3
# vim: textwidth=0 wrapmargin=0 tabstop=2 shiftwidth=2 softtabstop=2 smartindent smarttab

import argparse
import dateutil.parser
import dateutil.utils
import logging
import os
import pathlib
import pprint
import requests
import sys
import time
import yaml

pp = pprint.PrettyPrinter(indent=2, width=10000)

import org.miggy.edcapi

###########################################################################
# Logging
###########################################################################
os.environ['TZ'] = 'UTC'
time.tzset()
__default_loglevel = logging.INFO
__logger = logging.getLogger('fd-api')
__logger.setLevel(__default_loglevel)
__logger_ch = logging.StreamHandler()
__logger_ch.setLevel(__default_loglevel)
__logger_formatter = logging.Formatter('%(asctime)s;%(name)s;%(levelname)s;%(module)s.%(funcName)s: %(message)s')
__logger_formatter.default_time_format = '%Y-%m-%d %H:%M:%S';
__logger_formatter.default_msec_format = '%s.%03d'
__logger_ch.setFormatter(__logger_formatter)
__logger.addHandler(__logger_ch)
###########################################################################

###########################################################################
"""
 "  Configuration
"""
###########################################################################
__configfile_fd = os.open(pathlib.Path(sys.path[0]) / "fd-api-config.yaml", os.O_RDONLY)
__configfile = os.fdopen(__configfile_fd)
__config = yaml.load(__configfile)
if __config.get('user_agent') is None:
  __logger.error('You must set a "user_agent" in the config file')
  exit(-1)

###########################################################################

###########################################################################
# Command-Line Arguments
###########################################################################
__parser = argparse.ArgumentParser()
__parser.add_argument("--loglevel", help="set the log level to one of: DEBUG, INFO (default), WARNING, ERROR, CRITICAL")
__parser.add_argument("--rawoutput", action="store_true", help="Output raw returned data")
__parser.add_argument("--pts", action="store_true", help="Use PTS server, not live")

__parser_endpoints = __parser.add_mutually_exclusive_group(required=True)
__parser_endpoints.add_argument("--endpoints", action="store_true", help="Ask the CAPI server what the currently available endpoints are")
__parser_endpoints.add_argument("--profile", action="store_true", help="Request retrieval of Cmdr's profile")
__parser_endpoints.add_argument("--market", action="store_true", help="Request retrieval of market data")
__parser_endpoints.add_argument("--shipyard", action="store_true", help="Request retrieval of shipyard data")
__parser_endpoints.add_argument("--fleetcarrier", action="store_true", help="Request retrieval of fleetcarrier data")
__parser_endpoints.add_argument(
  "--journal",
  metavar="date",
  nargs="?",
  default=False,
  help="Request retrieval of journal data.  Defaults to 'today' if no 'date' is given, else the string is parsed per python dateutil.parser capabilities.",
)

__parser.add_argument("cmdrname", nargs=1, help="Specify the Cmdr Name for this Authorization")

__args = __parser.parse_args()
if __args.loglevel:
  __level = getattr(logging, __args.loglevel.upper())
  __logger.setLevel(__level)
  __logger_ch.setLevel(__level)

__logger.debug('Args: {!r}'.format(__args))
cmdrname = __args.cmdrname[0]
###########################################################################

###########################################################################
# Load a relevant Auth State
###########################################################################
def loadAuthState(cmdr: str) -> int:
  ########################################
  # Retrieve and test state
  ########################################
  db = edcapi.database(__logger, __config)
  auth_state = db.getActiveTokenState()
  if auth_state:
    ## Do we have an access_token, and does it work?
    if auth_state['access_token']:
      print("Found un-expired access_token, assuming it's good.")
      return(0)
    else:
      print("Un-expired access_token, but no access_token? WTF!")
      return(-1)
  else:
    print("No auth state with un-expired access_token found, continuing...")
  ########################################
###########################################################################

###########################################################################
# Main
###########################################################################
def main():
  __logger.debug("Start")

  # Set the required capi_url
  if __args.pts:
    __config['capi_url'] = __config['capi_urls']['pts']

  else:
    __config['capi_url'] = __config['capi_urls']['live']

  capi = org.miggy.edcapi.edcapi(__logger, __config)

  if __args.endpoints:
    rawep, ep = capi.endpoints.get(cmdrname)
    if __args.rawoutput:
      print(f'{rawep}\n')
    else:
      print(pprint.pformat(ep, width=79))

  if __args.profile:
    (rawprofile, profile) = capi.profile.get(cmdrname)
    if not profile:
      return -1

    if __args.rawoutput:
      print(rawprofile)
      print('')
    else:
      print(pp.pformat(profile))

  if __args.market:
    (rawmarket, market) = capi.market.get(cmdrname)
    if not market:
      return -1

    if __args.rawoutput:
      print(rawmarket)
      print('')
    else:
      print(pp.pformat(market))

  if __args.shipyard:
    (rawshipyard, shipyard) = capi.shipyard.get(cmdrname)
    if not shipyard:
      return -1

    if __args.rawoutput:
      print(rawshipyard)
      print('')
    else:
      print(pp.pformat(shipyard))

  if __args.fleetcarrier:
    (rawfleetcarrier, fleetcarrier) = capi.fleetcarrier.get(cmdrname)
    if not fleetcarrier:
      return -1

    if __args.rawoutput:
      print(rawfleetcarrier)
      print('')
    else:
      print(pp.pformat(fleetcarrier))

  # You get 'False' if not present at all, 'None' if no optional arg
  if __args.journal != False:
    # Validate the date format
    if __args.journal:
      try:
        j_date = dateutil.parser.parse(__args.journal)

      except Exception as e:
        __logger.error("Could not parse the string '{date}' into a date".format(date=__args.journal))
        return -1

    else:
      j_date = dateutil.utils.today()

    datestr = j_date.strftime("%Y/%m/%d")
    __logger.debug('Retrieving journals for date "{date}"'.format(date=datestr))
    rawjournal = capi.journal.get(cmdrname, datestr)
    if not rawjournal:
      return -1

    print('{journal}'.format(journal=rawjournal))

###########################################################################
if __name__ == '__main__':
  exit(main())
