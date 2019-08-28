#!/usr/bin/env python3
# vim: textwidth=0 wrapmargin=0 tabstop=2 shiftwidth=2 softtabstop smartindent

import os
import yaml, logging, argparse

import requests
import pprint
pp = pprint.PrettyPrinter(indent=2)

import edcapi

###########################################################################
"""
 "  Configuration
"""
###########################################################################
__configfile_fd = os.open("fd-api-config.yaml", os.O_RDONLY)
__configfile = os.fdopen(__configfile_fd)
__config = yaml.load(__configfile, Loader=yaml.CLoader)
###########################################################################

###########################################################################
# Logging
###########################################################################
os.environ['TZ'] = 'UTC'
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
# Command-Line Arguments
###########################################################################
__parser = argparse.ArgumentParser()
__parser.add_argument("--loglevel", help="set the log level to one of: DEBUG, INFO (default), WARNING, ERROR, CRITICAL")
__parser.add_argument("cmdrname", nargs=1, help="Specify the Cmdr Name for this Authorization")
__parser.add_argument("--profile", action="store_true", help="Request retrieval of Cmdr's profile")
__args = __parser.parse_args()
if __args.loglevel:
  __level = getattr(logging, __args.loglevel.upper())
  __logger.setLevel(__level)
  __logger_ch.setLevel(__level)
cmdrname = __args.cmdrname[0]
###########################################################################

###########################################################################
# Load a relevant Auth State
###########################################################################
def loadAuthState(cmdr=None):
  ########################################
  # Retrieve and test state
  ########################################
  db = edcapi.database(__config.get('db_sqlite_file'), __logger)
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

  if not __args.profile:
    __logger.error("You must specify at least one action")

  db = edcapi.database(__config.get('db_sqlite_file'), __logger)
  auth_state = db.getActiveTokenState(cmdrname)
  if not auth_state:
    __logger.error('No un-expired Access Token found for this Commander.  Please run oauth2-pkce.py');
    return(-1)

  __logger.debug('Got an allegedly un-expired Access Token, continuing...')
  if __args.profile:
    edcapi_profile = edcapi.profile(db, __logger, __config)
    profile = edcapi_profile.get(cmdrname, auth_state['access_token'])
    if not profile:
      return(-1)

    print(pp.pformat(profile))

    # XXX: Need to do something with this that comes back ?
    # Set-Cookie: access_token=1566841911%7C%7HEXSTRING; domain=companion.orerve.net; path=/; expires=Mon, 26-Aug-2019 17:51:51 UTC; secure
    #  Looks like a refresh token in there ?
    #  That first number is a unix epoch timestamp from 24 hours ago.
###########################################################################
if __name__ == '__main__':
  exit(main())
