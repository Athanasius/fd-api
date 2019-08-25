import apsw
from apsw import SQLITE_OPEN_READWRITE as SQLITE_OPEN_READWRITE

###########################################################################
# Our base class for database operations
###########################################################################
class database(object):

  def __init__(self, sqlite_file, __logger):
    self.__logger = __logger
    self.__db = apsw.Connection(sqlite_file, flags=SQLITE_OPEN_READWRITE)
    self.__cursor = self.__db.cursor()

  def storeNewState(self, state, challenge, verifier):
    self.__logger.info("storeNewState: state='{}', challenge='{}', verifier='{}'".format(state, challenge, verifier))
    self.__cursor.execute("INSERT INTO auth (state,challenge,verifier) VALUES(:state,:challenge,:verifier)", {"state":state, "challenge":challenge, "verifier":verifier})

  def getActiveTokenState(self):
    self.__logger.info('getActiveTokenState:')
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
      self.__logger.info('getActiveTokenState: Returning auth_state = \n{}'.format(auth_state))
      return auth_state
    else:
      return None

###########################################################################
