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

  def get(self, cmdrname, access_token):
    self.__logger.debug('Start')

    # Send request with Access Token
    uri = self.__config.get('capi_url') + '/profile'
    response = requests.get(uri,
      headers={
        "Authorization": "Bearer " + access_token,
        "Content-Type": "application/json"
      }
    )
    self.__profile = json.loads(response.text)
    self.__db.updateLastSuccessfulUse(cmdrname, access_token)

    return self.__profile
###########################################################################
