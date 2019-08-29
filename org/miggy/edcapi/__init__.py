from . import database as database
from . import profile as profile

###########################################################################
# Class for all edcapi operations
###########################################################################
class edcapi(object):

  #########################################################################
  # Constructor
  #########################################################################
  def __init__(self, logger, config):
    self.__logger = logger
    self.__logger.debug(".")
    self.__config = config

    self.__db = database.database(self.__logger, self.__config)
    self.profile = profile.profile(self.__db, self.__logger, self.__config)
  #########################################################################
