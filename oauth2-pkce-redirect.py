#!/usr/bin/env python3
# vim: textwidth=0 wrapmargin=0 tabstop=2 shiftwidth=2 softtabstop smartindent

import os
import yaml, logging, argparse

import json
import cgi
#import cgitb
#cgitb.enable(display=0, logdir="/var/www/user-rw/athan.fysh.org/fd-api-logs")

import urllib.request
import requests
import pprint
pp = pprint.PrettyPrinter(indent=2)

import ed_capi

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
__default_loglevel = logging.DEBUG
__logger = logging.getLogger('fd-api')
__logger.setLevel(__default_loglevel)
__logger_ch = logging.StreamHandler()
__logger_ch.setLevel(__default_loglevel)
__logger_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(module)s.%(funcName)s:\n%(message)s')
__logger_formatter.default_time_format = '%Y-%m-%d %H:%M:%S';
__logger_formatter.default_msec_format = '%s.%03d'
__logger_ch.setFormatter(__logger_formatter)
__logger.addHandler(__logger_ch)
###########################################################################

###########################################################################
# Command-Line Arguments
###########################################################################
#__parser = argparse.ArgumentParser()
#__parser.add_argument("--loglevel", help="set the log level to one of: DEBUG, INFO (default), WARNING, ERROR, CRITICAL")
#__args = __parser.parse_args()
#if __args.loglevel:
#  __level = getattr(logging, __args.loglevel.upper())
#  __logger.setLevel(__level)
#  __logger_ch.setLevel(__level)
##__logger_ch.setLevel(getattr(logging, 'DEBUG'))
###########################################################################

###########################################################################
# MAIN
###########################################################################
def main():
  __logger.debug('Start-Up')

  print('Content-Type: text/plain')
  print()
  ########################################
  # Check the received code
  ########################################
  getparams = cgi.FieldStorage()
  #cgi.test()
  print("getparams:\n{}\n".format(getparams))
  if 'code' not in getparams:
    __logger.error("No 'code' received")
    return(-1)
  auth_code = getparams['code'].value
  if 'state' not in getparams:
    __logger.error("No 'state' received")
    return(-1)
  state_recv = getparams['state'].value
  ####
  # Retrieve state
  ####
  db = ed_capi.database(__config.get('db_sqlite_file'), __logger)
  if not db:
    __logger.error('Failed to open auth state database')
  auth_state = db.getAuthState(state_recv)
  print('Auth State from db:\n{}'.format(auth_state))
  ####

  if auth_state and state_recv != auth_state['state']:
    __logger.error("Received state doesn't match the stored one")
    return(-2)
  __logger.info("Auth Code: '{}'".format(auth_code))
  __logger.info("Received State: '{}'".format(state_recv))
  ########################################


  ########################################
  # Make a Token Request
  ########################################
  uri = __config.get('auth_api_url') + '/token'
  data = {
    'grant_type': 'authorization_code',
    'code': auth_code,
    'redirect_uri': __config.get('redirect_uri'),
    'client_id': __config.get('clientid'),
    'code_verifier': auth_state['verifier']
  }
# Worked:
#   Content-Type: application/x-www-form-urlencoded
#   redirect_uri=https%3A%2F%2Fed.miggy.org%2Ffd-api%2Foauth2-pkce-redirect.py&code=f68ec9f8-5355-4c30-9319-33495c506e8c&grant_type=authorization_code&code_verifier=b9b-J9s8JcQ5hAIB7YL919Ht9TSTVN4AAe_C3lMWVwE=&client_id=9d6b78c7-c968-43a4-b020-ffcf26d1985f
  req_data = ""
  for d in data.keys():
    if d == 'redirect_uri':
      req_data = req_data + urllib.parse.urlencode({d:data[d]}) + "&"
    else:
      req_data = req_data + d + "=" + data.get(d) + "&"
  req_data = req_data[0:-1]
  ### req_data = urllib.parse.urlencode(data)
  req_data = req_data.encode('ascii')
  print("req_data:\n{}\n".format(req_data))
  #return(0)
  ### import http.client as http_client
  ### http_client.HTTPConnection.debuglevel = 1
  ### requests_log = logging.getLogger("requests.packages.urllib3")
  ### requests_log.setLevel(logging.DEBUG)
  ### requests_log.propagate = True

  response = requests.post(uri, data=req_data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
  tokens = json.loads(response.text)
  print(response.text)
  ########################################

###########################################################################

if __name__ == '__main__':
      main()
