# vim: textwidth=0 wrapmargin=0 tabstop=2 shiftwidth=2 softtabstop=2 smartindent smarttab
import requests
from logging import Logger
from typing import Dict, Optional
from yaml import YAMLObject

from . import database as database
from . import endpoints as endpoints
from . import profile as profile
from . import market as market
from . import shipyard as shipyard
from . import fleetcarrier as fleetcarrier
from . import journal as journal
from . import communitygoals as communitygoals

###########################################################################
# Class for all edcapi operations
###########################################################################
class edcapi(object):

  #########################################################################
  # Constructor
  #########################################################################
  def __init__(self, logger: Logger, config: YAMLObject):
    self.__logger = logger
    self.__logger.debug(".")
    self.__config = config

    self.__db = database.database(self.__logger, self.__config)
    self.endpoints = endpoints.endpoints(self.__db, self.__logger, self.__config)
    self.profile = profile.profile(self.__db, self.__logger, self.__config)
    self.market = market.market(self.__db, self.__logger, self.__config)
    self.shipyard = shipyard.shipyard(self.__db, self.__logger, self.__config)
    self.fleetcarrier = fleetcarrier.fleetcarrier(self.__db, self.__logger, self.__config)
    self.journal = journal.journal(self.__db, self.__logger, self.__config)
    self.communitygoals = communitygoals.communitygoals(self.__db, self.__logger, self.__config)
  #########################################################################


  #########################################################################
  # Decode the latest Access Token for the given Commander
  #########################################################################
  def decode(self, cmdr: str) -> str:  # -> Optional[Dict]:
    token_type, access_token = self.__db.getLatestAccessToken(cmdr)

    if token_type is None:
      return None

    self.__logger.debug(f'Access Token being decoded:\n{access_token}\n')
    # Send request with Access Token
    uri = 'https://auth.frontierstore.net/decode'
    response = requests.get(uri,
      headers={
        "User-Agent": self.__config.get('user_agent'),
        "Authorization": "%s %s" % (token_type, access_token),
        "Content-Type": "application/json"
      }
    )

    return response.text

  #########################################################################
