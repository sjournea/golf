""" db_mongo.py """
import json
import logging

from pymongo import MongoClient
from common import printf

from tl_logger import TLLog 
log = TLLog.getLogger( 'mongo' )

class Collection(object):
  def __init__(self, mongo, db_name, coll_name):
    self.mongo = mongo
    self.db_name = db_name
    self.coll_name = coll_name
    self.db = mongo.conn[str(db_name)]
    self.coll = self.db[str(coll_name)]
    
  def clear(self):
    """ clear a collection in a database """
    log.debug( 'clear()')
    self.coll.remove({})

  def drop(self):
    """ drop a collection from a database """
    log.debug( 'drop()')
    self.db.drop_collection(self.coll_name)

  def count(self):
    """ return number of documents in collection """
    log.debug( 'count()')
    return self.coll.count()

  def insert(self, doc):
    """ insert a document """
    log.debug( 'insert() - doc:%s' % doc)
    return self.coll.insert(doc)

  def save(self, doc):
    """ Save a document into collection.
    Will either do an update or insert operation    
    """
    log.debug( 'save() - %s' % doc)
    return self.coll.save(doc)

  def remove(self, dct):
    """ Remove documents into collection.

    match on _id either do an update or insert operation    
    """
    log.debug( 'remove() - dct:%s' % (dct))
    return self.coll.remove(dct)

  def removeAll(self):
    """ Remove all documents from collection.

    Note: faster to drop collection.    
    """
    log.debug( 'removeAll()')
    return self.coll.remove({})

  def find_one(self, query=None):
    log.debug( 'find_one()')
    return self.coll.find_one(query)

  def find(self, query=None, skip=0, limit=0):
    """ drop a collection from a database """
    log.debug( 'find() - query:{} skip:{} limit:{}'.format(query, skip,limit))
    cur = None
    spec = {}
    if query:
      spec = query
    limit = int(limit)
    skip = int(skip)
    return self.coll.find(spec, skip=skip, limit=limit)

  def create_index(self, index):
    """ create an index """
    log.debug( 'create_index() - index:{0}'.format(index))
    self.coll.create_index(index)


class MongoSession(object):
  def __init__(self, conn):
    self.conn = conn

  
    
class MongoDB(object):
  """ class for mongo db usage """
  DEF_HOST = 'localhost'
  DEF_PORT = 27017

  def __init__(self, host=DEF_HOST, port=DEF_PORT):
    self.host = host
    self.port = port
    self._conn = None

  @property
  def conn(self):
    return self._conn
  
  def __enter__(self):
    if self._conn is not None:
      raise RuntimeError('%s already connected.' % self.__class__.__name__)
    try:
      log.debug( '__enter__() - host:%s port:%s' % (self.host,self.port))
      self._conn = MongoClient(host=self.host, port=self.port)
    except ConnectionFailure,ex:
      s = 'connect() fail - %s' % ex
      log.error( s )
      raise Exception( s )
    return MongoSession(self._conn)
  
  def __exit__(self, ex_ty, ex_val, tb):
    log.debug( '__exit__()')
    self._conn.close()
    self._conn = None
  
  def close(self):
    pass
  
  def make_collection(self, database_name, collection_name):
    return Collection(self, database_name, collection_name)

  def create_database(self, database_name, collection_name, dct):
    """ create a new database """
    log.debug( 'create_database() - database_name:{0} collection_name:{1}'.format(database_name,collection_name))
    db = self._conn[str(database_name)]
    co = db[str(collection_name)]
    obj_id = co.save(dct)

  def drop_database(self, database_name):
    """ create a new database """
    log.debug( 'drop_database() - database_name:{0}'.format(database_name))
    self._conn.drop_database(str(database_name))

  lstDBIgnore = ['local']
  lstCollIgnore = ['system.indexes']
  def databases(self, showAll=False):
    """ return a dictionaries of database names with list of collection namess """
    log.debug( 'databases() - showAll:%s' % showAll)
    dct = {}
    lstDBNames = self._conn.database_names()
    if not showAll:
      lstDBNames = [dbName for dbName in lstDBNames if dbName not in self.lstDBIgnore]
    for dbName in lstDBNames:
      db = self._conn[dbName]
      lstCollNames = db.collection_names()
      if not showAll:
        lstCollNames = [colName for colName in lstCollNames if colName not in self.lstCollIgnore]
      dct[dbName] = lstCollNames
    return dct

  def collection_clear(self, dbName, collName):
    """ clear a collection in a database """
    log.debug( 'drop_database() - dbName:{0} collName:{1}'.format(dbName,collName))
    db = self._conn[str(dbName)]
    co = db[str(collName)]
    co.remove({})

  def collection_drop(self, dbName, collName):
    """ drop a collection from a database """
    log.debug( 'collection_drop() - dbName:{0} collName:{1}'.format(dbName,collName))
    db = self._conn[str(dbName)]
    db.drop_collection(collName)

  def collection_count(self, dbName, collName):
    """ return number of documents in collection """
    log.debug( 'collection_count() - dbName:{0} collName:{1}'.format(dbName,collName))
    db = self._conn[str(dbName)]
    co = db[str(collName)]
    return co.count()

  def insert(self, dbName, collName, doc):
    """  insert a document """
    log.debug( 'insert() - dbName:{0} collName:{1}'.format(dbName,collName))
    obj = None
    db = self._conn[str(dbName)]
    co = db[str(collName)]
    obj = co.insert(doc)
    return obj

  def insert_many(self, dbName, collName, lstDocs):
    """Bulk insert documents """
    log.debug( 'insert_many() - dbName:{0} collName:{1}'.format(dbName,collName))
    db = self._conn[str(dbName)]
    co = db[str(collName)]
    return co.insert_many(lstDocs)

  def find_one(self, dbName, dbColl, query=None):
    """ drop a collection from a database """
    log.debug( 'find_one() - dbName:{0} collName:{1}'.format(dbName,dbColl))
    dct = None
    db = self._conn[str(dbName)]
    co = db[str(dbColl)]
    dct = co.find_one(query)
    return dct

  def find(self, dbName, collName, query=None, fields=None, skip=0, limit=0):
    """ drop a collection from a database """
    log.debug( 'find() - dbName:{0} collName:{1} query:{2} fields:{3} skip:{4} limit:{5}'.format(dbName,collName,query,fields,skip,limit))
    cur = None
    spec = {}
    if query:
      spec = query
    limit = int(limit)
    skip = int(skip)
    db = self._conn[str(dbName)]
    co = db[str(collName)]
    cur = co.find(spec=spec, fields=fields, skip=skip, limit=limit)
    return cur

  def create_index(self, ddName, collName, index):
    """  create an index """
    log.debug( 'create_index() - dbName:{0} collName:{1} index:{2}'.format(dbName,collName,index))
    obj = None
    db = self._conn[str(dbName)]
    co = db[str(collName)]
    co.create_index(index)
    return obj

if __name__ == '__main__':
  import datetime

  def showDatabases(showAll=False):
    # show databases
    dct = db.databases(showAll=showAll)
    log.info( '%d databases:' % len(dct))
    for key,value in dct.items():
      log.info('  %-10s : %s' % (key,value))

  # create console handler and set level to debug
  ch = logging.StreamHandler()
  ch.setLevel(logging.DEBUG)

  # create formatter
  formatter = logging.Formatter('%(asctime)s - %(name)8s - %(levelname)s - %(message)s')

  # add formatter to ch
  ch.setFormatter(formatter)

  # add ch to logger
  log.addHandler(ch)
  log.setLevel(logging.DEBUG)

  db = None
  try:
    log.info( 'starting main')
    #

    db = MongoDB() # default args will be localhost 
    showDatabases(True)

    # delete a database
    db.drop_database( 'test_db')

    # create a database
    dbName = 'test_db'
    dbColl = 'test_coll'
    doc = { "author": "Steve",
            "text": "This is a test",
            "tags": ["mongodb", "python", "pymongo"],
            "date": datetime.datetime.utcnow(),
            }

    db.create_database( dbName,dbColl, doc)
    showDatabases()

    # insert some docs
    for i in xrange(5):
      doc = { "author": "Steve",
              "text": "This is a test doc {0}".format(i+1),
              "tags": ["mongodb", "python", "pymongo"],
              "date": datetime.datetime.utcnow(),
              }
      db.insert(dbName,dbColl,doc )
    # bulk insert some docs
    lst = []
    for i in xrange(15):
      doc = { "author": "Steve",
              "text": "This is a test doc for bulk insert {0}".format(i+1),
              "tags": ["mongodb", "python", "pymongo"],
              "date": datetime.datetime.utcnow(),
              }
      lst.append(doc)
    db.insert(dbName,dbColl,lst )
    # find
    cur = db.find(dbName, dbColl)
    print 'Count',cur.count()
    print cur.explain()['nscanned']
    for dct in cur:
      print dct
    # find one
    dct = db.find_one(dbName, dbColl, query={ 'text' : 'This is a test doc for bulk insert 1' })
    print dct
  finally:
    if db:
      db.close()
