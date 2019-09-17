#!/usr/bin/env python3
# vim: textwidth=0 wrapmargin=0 tabstop=2 shiftwidth=2 softtabstop=2 smartindent smarttab

import os
import yaml, logging, argparse

import random, base64, hashlib
import json
import cgi
#import cgitb
#cgitb.enable(display=0, logdir="/var/www/user-rw/athan.fysh.org/fd-api-logs")

import urllib.request
import requests
import pprint
pp = pprint.PrettyPrinter(indent=2)

import org.miggy.edcapi

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
# MAIN
###########################################################################
def main():
  __logger.debug('Start-Up')

  if not os.getenv('GATEWAY_INTERFACE'):
    handleCLI()
  else:
    handleCGI()

###########################################################################
# Being called from command-line
###########################################################################
def handleCLI():
  #########################################
  # Command-Line Arguments
  #########################################
  __parser = argparse.ArgumentParser()
  __parser.add_argument("--loglevel", help="set the log level to one of: DEBUG, INFO (default), WARNING, ERROR, CRITICAL")
  __parser.add_argument("cmdrname", nargs=1, help="Specify the Cmdr Name for this Authorization")
  __args = __parser.parse_args()
  cmdrName = __args.cmdrname[0]
  if __args.loglevel:
    __level = getattr(logging, __args.loglevel.upper())
    __logger.setLevel(__level)
    __logger_ch.setLevel(__level)

  #########################################

  ########################################
  # Retrieve and test state
  ########################################
  db = org.miggy.edcapi.database.database(__logger, __config)
  __logger.debug("cmdrName: '{}'".format(cmdrName))
  auth_state = db.getActiveTokenState(cmdrName)
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

  ########################################
  # Generate Code Verifier
  ########################################
  verifier = random.SystemRandom().getrandbits(8 * 32)
  __logger.debug('raw verifier: {}'.format(verifier))
  # We need a Base64, URL safe, version of this. NB: the '=' on the end is
  # OK in this instance.
  verifier_b64 = base64.urlsafe_b64encode(verifier.to_bytes(32, byteorder='big'))
  __logger.debug('b64 verifier: {}'.format(verifier_b64))
  ########################################

  ########################################
  # Generate Code Challenge
  ########################################
  # Using the URL-safe Base64 version of verifier, with the '=' still on the
  # end
  challenge = hashlib.sha256(verifier_b64).digest()
  __logger.debug('raw challenge: {}'.format(challenge))
  challenge_b64 = base64.urlsafe_b64encode(challenge)
  __logger.debug('b64 challenge: {}'.format(challenge_b64))
  challenge_b64_str = challenge_b64.decode().replace('=','')
  __logger.debug('str challenge: {}'.format(challenge_b64_str))
  ########################################


  ########################################
  # Generate 'State'
  ########################################
  state = random.SystemRandom().getrandbits(8 * 32)
  __logger.debug('raw state: {}'.format(state))
  #state_b64 = base64.b64encode(state.to_bytes(32, byteorder='big'))
  state_b64 = base64.urlsafe_b64encode(state.to_bytes(32, byteorder='big'))
  __logger.debug('b64 state: {}'.format(state_b64))
  state_b64_str = state_b64.decode().replace('=','')
#.replace('+','-').replace('/','_').replace('=','')
  __logger.debug('str state: {}'.format(state_b64_str))
  ########################################


  ########################################
  # Store state and the codes for when redirect_uri is called
  ########################################
  db.storeNewState(state_b64_str, challenge_b64.decode(), verifier_b64.decode(), cmdrName)
  ########################################

  ########################################
  # Get the User's Authorization
  ########################################
  __logger.debug("auth_api_url: '{}'".format(__config.get('auth_api_url')))
  request_uri = (__config.get('auth_api_url') +
      '/auth?audience=frontier'
      '&scope=auth%20capi'
      '&response_type=code'
      '&client_id=' + __config.get('clientid') +
      '&code_challenge=' + challenge_b64_str +
      '&code_challenge_method=S256'
      '&state=' + state_b64_str +
      '&redirect_uri=' + __config.get('redirect_uri')
  )
  print('Go to the following URL and Authorize the Application:\n\n{}\n'.format(request_uri))
  return(0)
  ########################################
###########################################################################

###########################################################################
# Being called as CGI
###########################################################################
def handleCGI():
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
  db = org.miggy.edcapi.database.database(__logger, __config)
  if not db:
    __logger.error('Failed to open auth state database')
  auth_state = db.getAuthState(state_recv)
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
  req_data = ""
  for d in data.keys():
    if d == 'redirect_uri':
      req_data = req_data + urllib.parse.urlencode({d:data[d]}) + "&"
    else:
      req_data = req_data + d + "=" + data.get(d) + "&"
  req_data = req_data[0:-1]
  req_data = req_data.encode('ascii')
  print("req_data:\n{}\n".format(req_data))
  #return(0)
  ### import http.client as http_client
  ### http_client.HTTPConnection.debuglevel = 1
  ### requests_log = logging.getLogger("requests.packages.urllib3")
  ### requests_log.setLevel(logging.DEBUG)
  ### requests_log.propagate = True

  response = requests.post(uri, data=req_data,
    headers={
      'Content-Type': 'application/x-www-form-urlencoded',
      'User-Agent': __config.get('user_agent')
    }
  )
  tokens = json.loads(response.text)
  print(response.text)
  ########################################

  ########################################
  # Update stored data with the access_token, refresh_token and expires
  ########################################
  db.updateWithAccessToken(
    state_recv,
    tokens['access_token'],
    tokens['refresh_token'],
    tokens['expires_in']
  )
  ########################################

  ########################################
  # Retrieve /decode so we know who this Access Token is for
  ########################################
  uri = __config.get('auth_api_url') + '/decode'
  session = requests.Session()
  session.headers.update(
    {
      'User-Agent': __config.get('user_agent'),
      "Authorization": "Bearer " + tokens["access_token"],
      "Content-Type": "application/json"
    }
  )
  response = session.get(uri)
  decode = json.loads(response.text)
  print(response.text)
  db.updateWithCustomerID(tokens['access_token'], decode['usr']['customer_id'])
  ########################################
###########################################################################

if __name__ == '__main__':
      main()
