import requests
import json

###########################################################################
# Our base class for profile operations
###########################################################################
class profile(object):

  #########################################################################
  #########################################################################
  def __init__(self, db, logger, config):
    self.__logger = logger
    self.__logger.debug(".")
    self.__db = db
    self.__config = config
  #########################################################################

  def get(self, cmdrname):
    self.__logger.debug('Start')

    # Get the Access Token
    access_token = self.__db.getAccessToken(cmdrname)
    if not access_token:
      self.__logger.critical("No Access Token, you'll need to auth from scratch again")
      return None
    # Send request with Access Token
    uri = self.__config.get('capi_url') + '/profile'
    response = requests.get(uri,
      headers={
        "User-Agent": self.__config.get('user_agent'),
        "Authorization": "Bearer " + access_token,
        "Content-Type": "application/json"
      }
    )
    self.__profile = None
    if response.status_code == 200:
      self.__profile = json.loads(response.text)
      self.__db.updateLastSuccessfulUse(cmdrname, access_token)
      self.__logger.debug("Success, headers = \n{}".format(response.headers))
    elif response.status_code == 206:
      self.__logger.error("Got 206, but this isn't a journal request!")
    elif r_status_code == 422: # Unprocessable Entity
      self.__logger.warn("HTTP Status 422 - Access Token expired?")
    else:
      self.__logger.critical("Got HTTPS Status: {}".format(response.status_code))

    return self.__profile
###########################################################################
