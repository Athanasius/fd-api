import apsw
from apsw import SQLITE_OPEN_READWRITE as SQLITE_OPEN_READWRITE

import datetime

###########################################################################
# Our base class for database operations
###########################################################################
class database(object):

  #########################################################################
  #########################################################################
  def __init__(self, sqlite_file, __logger):
    self.__logger = __logger
    self.__logger.debug("ed_capi.database: __init__")
    self.__db = apsw.Connection(sqlite_file, flags=SQLITE_OPEN_READWRITE)
    self.__cursor = self.__db.cursor()
  #########################################################################

  #########################################################################
  # Store a new state, along with its challenge and verifier
  #########################################################################
  def storeNewState(self, state, challenge, verifier):
    self.__logger.debug("storeNewState: state='{}', challenge='{}', verifier='{}'".format(state, challenge, verifier))
    self.__cursor.execute("INSERT INTO auth (state,challenge,verifier) VALUES(:state,:challenge,:verifier)", {"state":state, "challenge":challenge, "verifier":verifier})
  #########################################################################

  #########################################################################
  # Update an existing state-identified row with:
  #
  #   access_token
  #   refresh_token
  #   expires_in - This will be in seconds from 'now'(ish), so needs
  #                conversion
  #########################################################################
  def updateWithAccessToken(self, state, access_token, refresh_token, expires_in):
    self.__logger.debug("state='{}', access_token='{}', refresh_token='{}', expires_in='{}'".format(state, access_token, refresh_token, expires_in))
    now = datetime.datetime.now()
    # Fudge factor of 10 seconds in case processing took a while
    expires_dt = now + datetime.timedelta(0, expires_in - 10)
    expires = str(expires_dt)
    self.__cursor.execute(
      "UPDATE auth SET access_token = :access_token, refresh_token = :refresh_token, expires = :expires WHERE state = :state",
      {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires": expires,
        "state": state
      }
    )
  #########################################################################

  #########################################################################
  # Update an existing state, identified by Access Token, with
  # account information
  #########################################################################
  def updateWithCustomerID(self, access_token, customer_id):
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
  def getActiveTokenState(self):
    self.__logger.debug('getActiveTokenState:')
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
  # Get an auth state that matches a given state token
  #########################################################################
  def getAuthState(self, state=None):
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

###########################################################################
