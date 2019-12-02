# vim: textwidth=0 wrapmargin=0 tabstop=2 shiftwidth=2 softtabstop=2 smartindent smarttab
import apsw
from apsw import SQLITE_OPEN_READWRITE as SQLITE_OPEN_READWRITE

import datetime
import requests, json

from typing import Optional
from logging import Logger
from yaml import YAMLObject

###########################################################################
# Our base class for database operations
###########################################################################
class database:

  #########################################################################
  #########################################################################
  def __init__(self, logger: Logger, config: YAMLObject):
    self.__logger = logger
    self.__logger.debug(".")
    self.__config = config
    self.__db = apsw.Connection(self.__config.get('db_sqlite_file'), flags=SQLITE_OPEN_READWRITE)
    self.__cursor = self.__db.cursor()
  #########################################################################

  #########################################################################
  # Store a new state, along with its challenge and verifier
  #########################################################################
  def storeNewState(self, state: str, challenge: str, verifier:str, cmdrname: str):
    self.__logger.debug("storeNewState: state='{}', challenge='{}', verifier='{}', cmdrname='{}'".format(state, challenge, verifier, cmdrname))
    self.__cursor.execute("INSERT INTO auth (state, challenge, verifier, cmdr_name) VALUES(:state, :challenge, :verifier, :cmdr_name)", {"state":state, "challenge":challenge, "verifier":verifier, "cmdr_name":cmdrname})
  #########################################################################

  #########################################################################
  # Update an existing state-identified row with:
  #
  #   access_token
  #   refresh_token
  #   expires_in - This will be in seconds from 'now'(ish), so needs
  #                conversion
  #########################################################################
  def updateWithAccessToken(self, state: str, token_type: str, access_token: str, refresh_token: str, expires_in: int):
    self.__logger.debug("state='{}', token_type='{}', access_token='{}', refresh_token='{}', expires_in='{}'".format(state, token_type, access_token, refresh_token, expires_in))
    now = datetime.datetime.now()
    # Fudge factor of 10 seconds in case processing took a while
    expires_dt = now + datetime.timedelta(0, expires_in - 10)
    expires = str(expires_dt)
    self.__cursor.execute(
      "UPDATE auth SET token_type = :token_type, access_token = :access_token, refresh_token = :refresh_token, expires = :expires WHERE state = :state",
      {
        "token_type": token_type,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires": expires,
        "state": state
      }
    )
  #########################################################################

  #########################################################################
  # Update with a just refreshed Access Token
  #########################################################################
  def updateWithRefreshedAccessToken(self, token_type: str, access_token: str, expires_in: int, refresh_token_old: str, refresh_token_new: str):
    self.__logger.debug("token_type='{}', access_token='{}', expires_in='{}', refresh_token_old='{}', refresh_token_new='{}'".format(token_type, access_token, expires_in, refresh_token_old, refresh_token_new))
    now = datetime.datetime.now()
    # Fudge factor of 10 seconds in case processing took a while
    expires_dt = now + datetime.timedelta(0, expires_in - 10)
    expires = str(expires_dt)
    self.__cursor.execute(
      "UPDATE auth SET token_type = :token_type, access_token = :access_token, refresh_token = :refresh_token_new, expires = :expires WHERE refresh_token = :refresh_token_old",
      {
        "token_type": token_type,
        "access_token": access_token,
        "refresh_token_new": refresh_token_new,
        "expires": expires,
        "refresh_token_old": refresh_token_old
      }
    )
  #########################################################################

  #########################################################################
  # Update an existing state, identified by Access Token, with
  # account information
  #########################################################################
  def updateWithCustomerID(self, access_token: str, customer_id: int):
    self.__logger.debug("access_token='{}', customer_id='{}'".format(access_token, customer_id))
    self.__cursor.execute(
      "UPDATE auth SET customer_id = :customer_id WHERE access_token = :access_token",
      {
        "access_token": access_token,
        "customer_id": customer_id
      }
    )
  #########################################################################

  #########################################################################
  # Get the entire state of an active access_token
  #########################################################################
  def getActiveTokenState(self, cmdrname: str) -> dict:
    self.__logger.debug("getActiveTokenState: cmdrname='{}'".format(cmdrname))
    if cmdrname:
      self.__cursor.execute("SELECT * FROM auth WHERE cmdr_name = :cmdrname AND expires > datetime() ORDER BY id DESC LIMIT 1", {"cmdrname": cmdrname})
    else:
      self.__cursor.execute("SELECT * FROM auth WHERE expires > datetime() ORDER BY id DESC LIMIT 1")
    row = self.__cursor.fetchone()
    if row:
      desc = self.__cursor.getdescription()
      # column[0] will be the column name
      auth_state = dict(
        zip(
          (column[0] for column in desc),
          row
        )
      )
      self.__logger.debug('getActiveTokenState: Returning auth_state = \n{}'.format(auth_state))
      return auth_state
    else:
      self.__logger.debug('getActiveTokenState: Un-expired access_token found')
      return None
  #########################################################################

  #########################################################################
  # Get just a currently valid Access Token, if possible, for the given
  # cmdrname
  #########################################################################
  def getAccessToken(self, cmdrname: str) -> str:
    self.__logger.debug("cmdrname='{}'".format(cmdrname))
    self.__cursor.execute("SELECT token_type, access_token FROM auth WHERE cmdr_name = :cmdrname AND expires > datetime() ORDER BY id DESC LIMIT 1", {"cmdrname": cmdrname})
    row = self.__cursor.fetchone()
    if row:
      self.__logger.debug("Returning Access Token of type '{}' =\n{}".format(row[0], row[1]))
      return (row[0], row[1])
    else: # Try Refresh
      self.__logger.debug('Access Token is expired, trying Refresh Token...')
      self.__cursor.execute("SELECT refresh_token FROM auth WHERE cmdr_name = :cmdrname ORDER BY id DESC LIMIT 1", {"cmdrname": cmdrname})
      row = self.__cursor.fetchone()
      if row:
        refresh_token_old = row[0]
        self.__logger.debug("Retrieved Refresh Token = '{}'".format(refresh_token_old))
        uri = self.__config.get('auth_api_url') + '/token'
        response = requests.post(uri,
          data={
            "grant_type": "refresh_token",
            "client_id": self.__config.get('clientid'),
            "refresh_token": refresh_token_old
          },
          ## PKCE Clients are considered unsafe for Shared Keys, so they're not used.
          #"client_secret": self.__config.get('shared_key'),
          headers={
            "User-Agent": self.__config.get('user_agent'),
          }
        )
        if response.status_code == 200:
          self.__logger.debug('Got new Access Token from Refresh Token')
          tokens = json.loads(response.text)
          self.updateWithRefreshedAccessToken(
            tokens['token_type'],
            tokens['access_token'],
            tokens['expires_in'],
            refresh_token_old,
            tokens['refresh_token']
          )
          self.__logger.debug('Returning Access Token =\n{}'.format(row[0]))
          return (tokens['token_type'], tokens['access_token'])
        else:
          self.__logger.critical("Failed to use Refresh Token: {}".format(response.status_code))
          return None
        # 401 - expired?
        # 500 - Just an error
      else: # No Refresh Token!
        self.__logger.critical("No Refresh Token for cmdrname = '{}'".format(cmdrname))
        return None

  #########################################################################

  #########################################################################
  # Get an auth state that matches a given state token
  #########################################################################
  def getAuthState(self, state: str) -> dict:
    self.__logger.debug('getAuthState: {}'.format(state))
    self.__cursor.execute("SELECT * FROM auth WHERE access_token IS NULL AND state = :state", {"state": state})
    row = self.__cursor.fetchone()
    if row:
      desc = self.__cursor.getdescription()
      auth_state = dict(zip((column[0] for column in desc), row))
      self.__logger.debug('getAuthState: Returning auth_state = \n{}'.format(auth_state))
      return auth_state
    else:
      self.__logger.debug('getAuthState: No matching state found')

    return None
  #########################################################################

  #########################################################################
  # Update when an Access Token was last successfully used
  #########################################################################
  def updateLastSuccessfulUse(self, cmdrname: str, access_token: str):
    self.__cursor.execute("UPDATE auth SET last_success = datetime() WHERE cmdr_name = :cmdrname AND access_token = :access_token", {"cmdrname":cmdrname, "access_token":access_token})
  #########################################################################
###########################################################################
