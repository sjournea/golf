#!/usr/bin/env python
""" dbmain.py - simple query test program for database """ 
#import sys
import logging
#import ConfigParser
import traceback
import threading
#import time,datetime,re,os,traceback,pdb

from golf_db.test_data import GolfCourseTestData, GolfPlayerTestData
from golf_db.course import GolfPlayer, GolfCourse, GolfHole
from util.db_mongo import MongoDB
from util.menu import MenuItem, Menu, InputException
from util.tl_logger import TLLog,logOptions

TLLog.config( 'logs\\dbmain.log', defLogLevel=logging.INFO )

#from SNTrack.const import *
#from SNTrack.master import Master
#from util.db_postgres import DBException
#from util.common import parseTimeString
#from util.common import toInt,flatten

log = TLLog.getLogger( 'dbmain' )

class GolfMenu(Menu):
  def __init__(self, mongo_db, cmdFile=None):
    super(GolfMenu, self).__init__(cmdFile)
    self.db = mongo_db
    self.database = None
    # add menu items
    self.addMenuItem( MenuItem( 'li', '',             'Show databases.' ,                   self._showDatabases) )
    self.addMenuItem( MenuItem( 'td', '<database>',   'create golf test data database.',    self._createGolfDatabase) )
    self.addMenuItem( MenuItem( 'dr', '<database>',   'Drop a database.',                   self._dropDatabase) )
    self.addMenuItem( MenuItem( 'use', '<database>',  'Use a database.',                    self._useDatabase) )
    ##self.addMenuItem( MenuItem( 'co', '',      'Execute a commit', self._commit))
    ##self.addMenuItem( MenuItem( 'f1', '',      'fetch one result', self._fetchone))
    ##self.addMenuItem( MenuItem( 'fa', '',      'fetch all results', self._fetchall))
    #self.addMenuItem( MenuItem( 'ta', '',      'Show tables', self._showTables))
    #self.addMenuItem( MenuItem( 'qc', '<where clause> <limit int> <order clause>', 'query container table', self._dbSelectContainer))
    #self.addMenuItem( MenuItem( 'qs', '<where clause> <limit int> <order clause>', 'query shipped table', self._dbSelectShipped))
    #self.addMenuItem( MenuItem( 'qh', '<where clause> <limit int> <order clause>', 'query history table', self._dbSelectHistory))
    #self.addMenuItem( MenuItem( 'uc', '<item label | cont_id id> <where clause> <limit int> <order clause>', 'update a container', self._dbUpdateContainer))
    #self.addMenuItem( MenuItem( 'sc', '<item label | cont_id id> <ship_id id | ship_desc desc> <ship_date date>', 'ship a container', self._dbShipContainer))
    #self.addMenuItem( MenuItem( 'ca', '', 'test adding a DB callback', self._dbExeCallbackAdd))
    #self.addMenuItem( MenuItem( 'cr', '', 'test removing a DB callback', self._dbExeCallbackRemove))
    #self.addMenuItem( MenuItem( 'va', '', 'validate database', self._dbValidate))
    self.updateHeader()

    # for wing IDE object lookup, code does not need to be run
    if 0:
      assert isinstance(self.db, MongoDB) 

  def updateHeader(self):
    self.header = 'Mongo DB - host:{} port:{} database:{}'.format(self.db.host, self.db.port, self.database)

  def _showDatabases(self):
    with self.db as db:
      dctDatabases = self.db.databases()
    for database, tables in dctDatabases.items():
      print '{:<15} : {}'.format(str(database), ','.join([str(tbl) for tbl in tables]))

  def _dropDatabase(self):
    if len(self.lstCmd) < 2:
      raise InputException( 'Not enough arguments for %s command' % self.lstCmd[0] )
    with self.db as db:
      self.db.drop_database(self.lstCmd[1])

  def _createGolfDatabase(self):
    if len(self.lstCmd) < 2:
      raise InputException( 'Not enough arguments for %s command' % self.lstCmd[0] )
    db_name = self.lstCmd[1]
    with self.db as db:
      self.db.drop_database(db_name)
      self.db.insert_many(db_name, 'players', GolfPlayerTestData)
      self.db.insert_many(db_name, 'courses', GolfCourseTestData)

  def _useDatabase(self):
    if len(self.lstCmd) < 2:
      raise InputException( 'Not enough arguments for %s command' % self.lstCmd[0] )
    self.database = self.lstCmd[1]
    self.updateHeader()

  #def _disconnect(self):
    #self.db.close()
    #self.updateHeader()

  #def _execute(self):
    #if len(self.lstCmd) < 2:
      #raise InputException( 'Not enough arguments for %s command' % self.lstCmd[0] )
    #sql = ' '.join( self.lstCmd[1:] )
    #self.db.execute( sql )

  #def _commit(self):
    #self.db.commit()

  #def _fetchone(self):
    #resp = self.db.fetchone()
    #print resp

  #def _fetchall(self):
    #lst = self.db.fetchall()
    #for resp in lst:
      #print resp

  #def _showTables(self):
    #lstTables = self.db.showTables()
    #for tbl in lstTables:
      #print tbl

  #def _dbSelectTbl(self, tbl):
    #""" select on table and return Record objects """
    #lstWhere = []
    #order = None
    #limit = None
    #where = None
    #for n,cmd in enumerate(self.lstCmd[1:]):
      #if cmd == 'limit':
        #limit = int(self.lstCmd[n+2])
      #elif cmd == 'where':
        #lstWhere.append(self.lstCmd[n+2])
      #elif cmd == 'order':
        #order = self.lstCmd[n+2]
    ## select the jobs from Job table
    #if lstWhere:
      #where = ' and '.join(lstWhere)
    #return tbl.select(self.db,where=where,order=order,limit=limit)

  ##def _dbSelect(self, dbSelectFunc):
    ##""" select on table and return Record objects """
    ##lstWhere = []
    ##order = None
    ##limit = None
    ##where = None
    ##for n,cmd in enumerate(self.lstCmd[1:]):
      ##if cmd == 'limit':
        ##limit = int(self.lstCmd[n+2])
      ##elif cmd == 'where':
        ##lstWhere.append(self.lstCmd[n+2])
      ##elif cmd == 'order':
        ##order = self.lstCmd[n+2]
    ### select the jobs from Job table
    ##if lstWhere:
      ##where = ' and '.join(lstWhere)
    ##return dbSelectFunc(where=where,order=order,limit=limit)

  #def _dbSelectContainer(self):
    #""" select on container table and return ContainerRecord records """
    #show = False
    #for n,cmd in enumerate(self.lstCmd[1:]):
      #if cmd == 'show':
        #show = True

    #lstRecs = self._dbSelectTbl( self.master.tblContainer ) 
    #print 'Total records selected : %d' % len(lstRecs)
    #for n,rec in enumerate(lstRecs):
      #if show:
        #lstConts = self.master.tblContainer.select(self.db, where='cont=%d' % rec.id)
        #print '%5d : %d items -- %s' % (n+1, len(lstCounts),rec)
        #for i,recCont in enumerate(lstConts):
          #print '    %3d : %s' % (i+1,recCont)
      #else:
        #lstDBFields,lstCounts = self.master.tblContainer.count(self.db, where='cont=%d' % rec.id)
        #cnt = lstCounts[0][0]
        #print '%5d : %3d items -- %s' % (n+1, cnt ,rec)

  #def _dbSelectShipped(self):
    #""" select on container table and return ContainerRecord records """
    #lstRecs = self._dbSelectTbl( self.master.tblShipping ) 
    #print 'Total records selected : %d' % len(lstRecs)
    #for n,rec in enumerate(lstRecs):
      #print '%5d : %s' % (n+1,rec)

  #def _dbSelectHistory(self):
    #""" select on container table and return ContainerRecord records """
    #lstRecs = self._dbSelectTbl( self.master.tblHistory ) 
    #print 'Total records selected : %d' % len(lstRecs)
    #for n,rec in enumerate(lstRecs):
      #print '%5d : %5d %s %s %-10s %s' % (n+1, rec.id, rec.label_code, rec.trans_date, rec.trans_action, rec.trans_desc)

  #def _dbUpdateContainer(self):
    #""" Update container locations in the container table 
          #uc <item label | cont_id id> <where clause> <limit int> <order clause> update
        #item or id MUST be set, will use last set. 
    #"""
    #where = None
    #update = False
    #for n,cmd in enumerate(self.lstCmd[1:]):
      #if cmd == 'item':
        #where = "label_code = '%s'" % self.lstCmd[n+2]
      #elif cmd == 'cont_id':
        #where = 'id = %d' % int(self.lstCmd[n+2])
      #elif cmd == 'update':
        #update = True
    ## 1st, get the target container
    #if not where:
      #raise InputException( 'item or cont_id MUST be used to select a target container')
    #recCont = self.master.tblContainer.get(self.db, where=where)

    ## 2nd, get containers using where, limit and order clauses
    #lstRecs = self._dbSelectTbl( self.master.tblContainer )
    #if not lstRecs:
      #raise InputException('No containers records selected to put into target container')

    #print 'Target Container : %s' % recCont
    #print 'Containers to Move : %d' % len(lstRecs)
    #for n,rec in enumerate(lstRecs):
      #print '  %5d : %s' % (n+1,rec)

    ## update all containers
    #if update:
      #for rec in lstRecs:
        #self.master.dbUpdateContainer(rec.label_code, recCont, commit=False)
      #self.db.commit()
    #else:
      #print 'Container update NOT PERFORMED'

  #def _dbShipContainer(self):
    #""" Ship a container to a shipping location 
          #sc <item label | id cont_id> <ship_id id | ship_desc desc> update
        #item or id MUST be set, will use last set. 
    #"""
    #where = None
    #update = False
    #ship_id = None
    #ship_desc = None
    #ship_date = None
    #for n,cmd in enumerate(self.lstCmd[1:]):
      #if cmd == 'item':
        #where = "label_code = '%s'" % self.lstCmd[n+2]
      #elif cmd == 'cont_id':
        #where = 'id = %d' % int(self.lstCmd[n+2])
      #elif cmd == 'ship_id':
        #ship_id = int(self.lstCmd[n+2])
      #elif cmd == 'ship_desc':
        #ship_desc = self.lstCmd[n+2]
      #elif cmd == 'ship_date':
        #ship_date = parseTimeString( self.lstCmd[n+2] )
      #elif cmd == 'update':
        #update = True
    ## 1st, get the shipping record
    #if ship_id is not None:
      #recShip = self.master.tblShipping.get( self.db, where='id=%d' % ship_id)
    #elif ship_desc is not None:
      #ship_id = self.master.dbInsertShipping( ship_desc, None, shipDate=ship_date )
      #recShip = self.master.tblShipping.get( self.db, where='id=%d' % ship_id)
    #else:
      #raise InputException( 'ship_id or ship_desc MUST be used to select a shipping container')

    ## 2nd, get the target container
    #if not where:
      #raise InputException( 'item or cont_id MUST be used to select the container to be shipped')
    #recCont = self.master.tblContainer.get(self.db, where=where)

    #print 'recCont : %s' % recCont
    #print 'recShip : %s' % recShip

    #if update:
      #self.master.dbUpdateShipping( recCont.id, recShip.id)

  #def _dbExeCallback1(self, sql, params):
    #print('CB1 sql:%s' % sql )
    #if params:
      #print('CB1 params:%s' % params )

  #def _dbExeCallback2(self, sql, params):
    #print('CB2 sql:%s' % sql )
    #if params:
      #print('CB2 params:%s' % params )

  #def _dbExeCallback3(self, sql, params):
    #print('CB3 sql:%s' % sql )
    #if params:
      #print('CB3 params:%s' % params )

  #def _dbExeCallbackAdd(self):
    #if len(self.lstCmd) < 2:
      #raise InputException( 'Not enough arguments for %s command' % self.lstCmd[0] )
    #func = None
    #if self.lstCmd[1] == '1':
      #func = self._dbExeCallback1
    #elif self.lstCmd[1] == '2':
      #func = self._dbExeCallback2
    #elif self.lstCmd[1] == '3':
      #func = self._dbExeCallback3

    #if func:
      #self.dbDef.ExecuteCallbackAdd(func) 

  #def _dbExeCallbackRemove(self):
    #if len(self.lstCmd) < 2:
      #raise InputException( 'Not enough arguments for %s command' % self.lstCmd[0] )

    #func = None
    #if self.lstCmd[1] == '1':
      #func = self._dbExeCallback1
    #elif self.lstCmd[1] == '2':
      #func = self._dbExeCallback2
    #elif self.lstCmd[1] == '3':
      #func = self._dbExeCallback3

    #if func:
      #self.dbDef.ExecuteCallbackRemove(func) 

  #def _dbValidate(self):
    #""" va """
    #updateTbl = False
    #for n,cmd in enumerate(self.lstCmd[1:]):
      #if cmd == 'update':
        #updateTbl = True
    #self.master.dbValidateTables(updateTables=updateTbl)

DEF_LOG_ENABLE = 'dbmain'
DEF_DB_HOST = MongoDB.DEF_HOST
DEF_DB_PORT = MongoDB.DEF_PORT
DEF_DATABASE = 'golf'

def main():
  # build the command line arguments
  from optparse import OptionParser
  parser = OptionParser()
  parser.add_option( "-o",  "--host", dest="db_host", default=DEF_DB_HOST,
                       help='Database host. Default is "%s"' % DEF_DB_HOST)
  parser.add_option( "-p",  "--port", dest="db_port", default=DEF_DB_PORT,
                       help='Database port. Default is "%s"' % DEF_DB_PORT)
  parser.add_option( "-d",  "--database", dest="database", default=DEF_DATABASE,
                       help='Set database to use. Default is ' )
  parser.add_option( "-m",  "--logEnable", dest="lstLogEnable", default=DEF_LOG_ENABLE,
                       help='Comma separated list of log modules to enable, * for all. Default is "%s"' % DEF_LOG_ENABLE)
  parser.add_option( "-g",  "--showLogs", action="store_true", dest="showLogs", default=False,
                       help='list all log options.' )
  parser.add_option( "-y",  "--runCmdFile", dest="cmdFile", default=None,
                       help="Run a command file at startup.")

  #  parse the command line and set values
  (options, args) = parser.parse_args()

  master = None
  try:
    # set the main thread name
    thrd = threading.currentThread()
    thrd.setName( 'dbmain' )

    log.info(80*"*")
    log.info( 'dbmain - starting' )
    logOptions(options.lstLogEnable, options.showLogs, log=log)

    # create MongoDB object
    db = MongoDB(host=options.db_host, port=options.db_port)

    # create menu application 
    menu = GolfMenu(db, options.cmdFile)
    menu.runMenu()

  except Exception, err:
    s = '%s: %s' % (err.__class__.__name__, err)
    log.error( s )
    print s

    print '-- traceback --'
    traceback.print_exc()
    print

  finally:
    log.info( 'dbmain - exiting' )
    TLLog.shutdown()        

if __name__ == '__main__':
  main()