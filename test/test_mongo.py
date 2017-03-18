import datetime
import unittest
from bson.objectid import ObjectId
from util.db_mongo import MongoDB,Collection

from util.tl_logger import TLLog
log = TLLog.getLogger('mongo')

class MongoTestCase(unittest.TestCase):
  pass
  #@classmethod
  #def setUpClass(cls):
    #log.enable()
    
  #@classmethod
  #def tearDownClass(cls):
    #log.disable()
    
class MongoDBCreateTest(MongoTestCase):
  def test_init(self):
    # check default parameters
    db = MongoDB()
    self.assertEqual(db.host, MongoDB.DEF_HOST)
    self.assertEqual(db.port, MongoDB.DEF_PORT)
    self.assertIsNone(db._conn)

    host = 'www.database.com' 
    port = 9876
    db = MongoDB(host=host, port=port)
    self.assertEqual(db.host, host)
    self.assertEqual(db.port, port)
    self.assertIsNone(db._conn)

  def test_connect(self):
    db = MongoDB()
    with db:
      self.assertIsNotNone(db._conn)

  def test_databases(self):
    db = MongoDB()
    with db:
      dct = db.databases()
      #print dct


class MongoDBTest(MongoTestCase):
  def setUp(self):
    self.db = MongoDB()
    self.database_name = 'test_db'
    self.collection_name = 'test_co'

  def tearDown(self):
    pass

  def test_databases(self):
    with self.db:
      dct = self.db.databases()

  def test_create_database(self):
    with self.db:
      dct = self.db.databases()
      if self.database_name in dct:
        self.db.drop_database(self.database_name)

      self.db.create_database(self.database_name, self.collection_name, {})
      dct = self.db.databases()
      self.assertIn(self.database_name, dct)

      self.db.drop_database(self.database_name)
      dct = self.db.databases()
      self.assertNotIn(self.database_name, dct)

  def test_create_collection(self):
    with self.db:
      # create a database
      dbName = 'test_db'
      dbColl = 'test_coll'
      doc = { "author": "Steve",
              "text": "This is a test",
              "tags": ["mongodb", "python", "pymongo"],
              "date": datetime.datetime.utcnow(),
              }
    
      self.db.create_database(dbName, dbColl, doc)
      dct = self.db.databases()
      self.assertIn(dbName, dct)

      self.db.drop_database(dbName)
      dct = self.db.databases()
      self.assertNotIn(dbName, dct)
      
class MongoDBCollectionTest(MongoTestCase):
  def setUp(self):
    self.db = MongoDB()
    self.database_name = 'test_db'
    self.collection_name = 'test_co'
    with self.db:
      self.db.drop_database(self.database_name)

  def tearDown(self):
    with self.db:
      self.db.drop_database(self.database_name)

  def test_collection_create(self):
    with self.db:
      coll = Collection(self.db, self.database_name, self.collection_name) 

  def test_collection_insert(self):
    doc = { "author": "Hammy",
            "text": "This is a test",
            "tags": ["mongodb", "python", "pymongo"],
            }
    with self.db:
      coll = Collection(self.db, self.database_name, self.collection_name) 
      coll.insert(doc)
      cur = coll.find()
      self.assertEquals(cur.count(), 1)
      dct = cur[0]
      for key,value in doc.iteritems():
        self.assertEqual(value, dct[key])
      self.assertIn('_id', dct)

  def test_collection_clear(self):
    """ test clear a collection in a database """
    with self.db:
      coll = Collection(self.db, self.database_name, self.collection_name) 
      coll.clear()
      self.assertEquals(coll.count(), 0)
      
  def test_collection_drop(self):
    """ test dropping a collection from a database """
    with self.db:
      coll = Collection(self.db, self.database_name, self.collection_name) 
      coll.drop()
      dct = self.db.databases()
      colls = dct[self.database_name]
      self.assertNotIn(self.collection_name, colls)

  def test_collection_count(self):
    """ test counting a collection from a database 
        also tests insert and remove    
    """
    with self.db:
      coll = Collection(self.db, self.database_name, self.collection_name) 
      self.assertEquals(coll.count(), 0)
      # add docs and check count
      for i in xrange(5):
        doc = { "author": "Steve",
                "key": "Key{0}".format(i+1),
                "tags": ["mongodb", "python", "pymongo"],
                "date": datetime.datetime.utcnow(),
                }
        coll.insert(doc)
        self.assertEquals(coll.count(), i+1)

      for n in xrange(5):
        doc = { "key": "Key{0}".format(n+1) }
        coll.remove(doc)
        self.assertEquals(coll.count(), (i+1)-(n+1))

  def test_collection_remove_all(self):
    """ test remove all from a collection 
    """
    with self.db:
      coll = Collection(self.db, self.database_name, self.collection_name) 
      # add docs 
      for i in xrange(5):
        doc1 = { "author": "Steve",
                 "key": "Key{0}".format(i+1),
               }
        doc2 = { "author": "Ruby",
                 "key": "Key{0}".format(i+1),
                 }
        coll.insert(doc1)
        coll.insert(doc2)
      self.assertEquals(coll.count(), 10)
      coll.removeAll()
      self.assertEquals(coll.count(), 0)

  def test_collection_remove_multiple(self):
    """ test remove all from a collection 
    """
    with self.db:
      coll = Collection(self.db, self.database_name, self.collection_name) 
      # add docs 
      for i in xrange(5):
        doc1 = { "author": "Steve",
                 "key": "Key{0}".format(i+1),
               }
        doc2 = { "author": "Ruby",
                 "key": "Key{0}".format(i+1),
                 }
        doc3 = { "author": "Perl",
                 "key": "Key{0}".format(i+1),
                 }
        coll.insert(doc1)
        coll.insert(doc2)
        coll.insert(doc3)
      self.assertEquals(coll.count(), 15)
      coll.remove({ 'author': 'Steve'})
      self.assertEquals(coll.count(), 10)
      coll.remove({ 'author': 'Ruby'})
      self.assertEquals(coll.count(), 5)

  def test_collection_find(self):
    rec_count = 5
    with self.db:
      coll = Collection(self.db, self.database_name, self.collection_name)
      # find an empty collection
      cursor = coll.find()
      self.assertEqual(cursor.count(), 0)
      # find_one on empty collection
      dct = coll.find_one()
      self.assertIsNone(dct)
      # add some docs 
      lstAuthors = ['Steve', 'Ruby', 'Perl']
      lstKeys = ['Key{0}'.format(i+1) for i in xrange(rec_count)]
      total_recs = rec_count*len(lstAuthors)
      for i in xrange(rec_count):
        for author in lstAuthors:
          doc = { "author": author,
                   "key": "Key{0}".format(i+1),
                   "_id": ObjectId(),
                 }
          coll.insert(doc)
      self.assertEquals(coll.count(), total_recs)

      # test find_one()
      for author in lstAuthors:
        dct = coll.find_one({'author': author})
        self.assertEqual(len(dct), 3)
        self.assertEqual(dct['key'], 'Key1')
        self.assertEqual(dct['author'], author)
      # test find()
      cursor = coll.find()
      self.assertEqual(cursor.count(), total_recs)
      for author in lstAuthors:
        cursor = coll.find({'author': author})
        self.assertEqual(cursor.count(), rec_count)
        for dct in cursor:
          self.assertEqual(len(dct), 3)
          self.assertIn(dct['key'], lstKeys)
          self.assertEqual(dct['author'], author)

  def create_index(self, index):
    """ create an index """
    log.debug( 'create_index() - index:{0}'.format(index))
    self.coll.create_index(index)

  def test_collection_insert_nested(self):
    doc = { "author": "Hammy",
            "text": "This is a test",
            "tags": ["mongodb", "python", "pymongo"],
            "dict": {'key1': 1, 'key2': 2, 'key3': 3 },
            "list": [
                {'key1': 1, 'key2': 2, 'key3': 3 },
                {'key1': 4, 'key2': 5, 'key3': 9 },
            ],
            }
    with self.db:
      coll = Collection(self.db, self.database_name, self.collection_name) 
      coll.insert(doc)
      cur = coll.find()
      self.assertEquals(cur.count(), 1)
      dct = cur[0]
      for key,value in doc.iteritems():
        self.assertEqual(value, dct[key])
      self.assertIn('_id', dct)

      