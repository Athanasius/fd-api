# vim: textwidth=0 wrapmargin=0 tabstop=2 shiftwidth=2 softtabstop=2 smartindent smarttab
import requests
import json

import pprint
pp = pprint.PrettyPrinter(indent=2)

from logging import Logger
from yaml import YAMLObject

###########################################################################
# Our base class for profile operations
###########################################################################
class profile(object):

  #########################################################################
  #########################################################################
  def __init__(self, db, logger: Logger, config: YAMLObject):
    self.__logger = logger
    self.__logger.debug(".")
    self.__db = db
    self.__config = config
  #########################################################################

  def get(self, cmdrname: str) -> dict:
    self.__logger.debug('Start')

    # Get the Access Token
    (token_type, access_token) = self.__db.getAccessToken(cmdrname)
    if not access_token:
      self.__logger.critical("No Access Token, you'll need to auth from scratch again")
      return None

    # Send request with Access Token
    uri = self.__config.get('capi_url') + '/profile'
    response = requests.get(uri, stream=True,
      headers={
        "User-Agent": self.__config.get('user_agent'),
        "Authorization": "%s %s" % (token_type, access_token),
        "Content-Type": "application/json"
      }
    )
    self.__profile = None

    peer = getattr(response.raw._connection.sock, 'socket', None)
    if peer:
      peer = peer.getpeername()

    if response.status_code == 200:
      self.__raw_profile = response.text
      self.__profile = json.loads(self.__raw_profile)
      self.__db.updateLastSuccessfulUse(cmdrname, access_token)
      self.__logger.debug(f'Success\nConnected To: {peer}\nHeaders:\n{response.headers}')

    elif response.status_code == 206:
      self.__logger.error("Got 206, but this isn't a journal request!")

    elif response.status_code in [ 401, 422 ]:
      # NB: CAPI servers used to return '422 - unprocessable entity' when
      #     the Access Token you'd tried to use was expired.  After the
      #     'September Update' patch in Sep 2019 they changed to using
      #     '401 - unauthorised' for this.
      self.__logger.warn(f'HTTP Status {response.status_code} - Access Token expired: {response.content.decode(encoding="utf-8")}')

    elif response.status_code == 418: # I'm a teapot - down for maintenance
      self.__logger.critical("HTTP Status 418 - Servers probably down for maintenance: %s", response.text)

    else:
      self.__logger.critical(f'Got HTTPS Status: {response.status_code}')

    return (self.__raw_profile, self.__profile)
###########################################################################
