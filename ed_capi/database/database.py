from sqlalchemy import create_engine, desc, exc, event, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Text, text, Character
from sqlalchemy.sql.sqltypes import TIMESTAMP

###########################################################################
# Our base class for database operations
###########################################################################
class database(object):
  def __init__(self, url, __logger):
    db_engine = create_engine(url)
    Base.metadata.create_all(db_engine)
    self.Session = sessionmaker(bind=db_engine)
    self.__logger = __logger

  def insertMessage(self, json, schemaref, gatewaytimestamp, blacklisted, message_valid, schema_test):
    __attempts = 0
    __max_attempts = 3
    __attempt_sleep = 5
    while __attempts < __max_attempts:
      try:  
        db_msg = Message(
          message = json,
          blacklisted = blacklisted,
          message_valid = message_valid,
          schema_test = schema_test,
          schemaref = schemaref,
          gatewaytimestamp = gatewaytimestamp
        )
        session = self.Session()
        session.add(db_msg)
        session.commit()
        break
      except sqlalchemy.exc.OperationalError as ex:
        self.__logger.error("database.insertMessage(): Database OperationalError - Sleeping " + __attempt_sleep + " seconds then trying again...")
        __attempts += 1
        os.sleep(__attempt_sleep)
      except:
        raise
    if __attempts == __max_attempts:
      self.__logger.error("database.insertMessage(): Reached __max_attempts (" + __max_attempts + ") - message dropped")

  def getActiveToken(self):
    session = self.Session()
    results = session.query(Message.message).filter(Message.schemaref == archiveType).order_by(desc(Message.gatewaytimestamp)).limit(1)
    for r in results:
      return r.message['header']['expires']
###########################################################################

###########################################################################
# sqlalchemy definitions
###########################################################################
Base = declarative_base()

class Message(Base):
  __tablename__ = "auth"

  id = Column(Integer, autoincrement=True, primary_key=True)
	state = Column(Character)
	challenge = Column(Character)
	verifier = Column(Character)
  access_token = Column(Text)
  refresh_token = Column(Text)
  expires = Column(TIMESTAMP, nullable=False, index=True)
###########################################################################
