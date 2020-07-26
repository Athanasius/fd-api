# vim: textwidth=0 wrapmargin=0 tabstop=2 shiftwidth=2 softtabstop=2 smartindent smarttab
from . import database as database
from . import profile as profile
from . import market as market
from . import shipyard as shipyard
from . import fleetcarrier as fleetcarrier
from . import journal as journal
from logging import Logger
from yaml import YAMLObject

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
    self.profile = profile.profile(self.__db, self.__logger, self.__config)
    self.market = market.market(self.__db, self.__logger, self.__config)
    self.shipyard = shipyard.shipyard(self.__db, self.__logger, self.__config)
    self.fleetcarrier = fleetcarrier.fleetcarrier(self.__db, self.__logger, self.__config)
    self.journal = journal.journal(self.__db, self.__logger, self.__config)
  #########################################################################
