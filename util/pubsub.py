""" pubsub.py -- simple Publish/Subscribe implementation """
import logging

from tl_logger import TLLog 
log = TLLog.getLogger( 'pubsub' )

class PubSub(object):
  """ Simple Publish/Subscribe implementation 
  """
  def __init__(self, name='pubsub'):
    super(PubSub, self).__init__()
    self.name = name
    self._lstAllEvents = []
    self._dctSubEvents = {}
    self._lstAllEvents = []

  def subscribe(self, event, cbFunc):
    """ subscribe to an event """
    log.debug('subscribe() %s - event:%s cbFunc:%s' % (self.name,event,cbFunc))
    if event in self._dctSubEvents:
      lst = self._dctSubEvents[event]
      # check if callback already exists 
      if cbFunc in lst:
        log.warn('subscribe() - event:%s - callback already defined' % event)
      else:    
        lst.append( cbFunc )
    else:
      # no callbacks for this event -- add new entry to dict
      lst = [cbFunc]
      self._dctSubEvents[event] = lst

  def unsubscribe(self, event, cbFunc):
    """ unsubscribe to an event """
    log.debug('unsubscribe() %s - event:%s cbFunc:%s' % (self.name,event,cbFunc))
    if event in self._dctSubEvents:
      lst = self._dctSubEvents[event]
      if cbFunc in lst:
        lst.remove(cbFunc)
      else:
        log.warn('unsubscribe() - event:%s - callback was not subscribed' % event)
    else:
      log.warn('unsubscribe() - event:%s - has not subscriptions' % event)

  def subscribeList(self, lstEvents, cbFunc):
    """ subscribe to a list of events """
    for event in lstEvents:
      self.subscribe(event, cbFunc)

  def unsubscribeList(self, lstEvents, cbFunc):
    """ unsubscribe to an event """
    for event in lstEvents:
      self.unsubscribe(event, cbFunc)

  def subscribeAll(self, cbFunc):
    """ subscribe to all events """
    log.debug('subscribeAll() %s - cbFunc:%s' % (self.name,cbFunc))
    self._lstAllEvents.append(cbFunc)

  def unsubscribeAll(self, cbFunc):
    """ unsubscribe to all events """
    self._lstAllEvents.remove(cbFunc)

  def publish(self, event, dct=None):
    """ publist an event, call all subscribers """
    log.debug('publish() %s - event:%s dct:%s' % (self.name,event,dct))
    if dct is None:
      dct = {}
    # sent to subscribe to all events
    for cbFunc in self._lstAllEvents:
      cbFunc(event, dct)
    # Use event type to send to callbacks
    if event in self._dctSubEvents:
      lst = self._dctSubEvents[event]
      for cbFunc in lst:
        cbFunc(event, dct)

  def __str__(self):
    return '%s _dctSubEvents:%s' % (self.name,self._dctSubEvents)

if __name__ == '__main__':

  class TestPubSub(object):
    def cb_1(self,event):
      print 'cb_1 - evt:%s' % event

    def cb_2(self,event):
      print 'cb_2 - evt:%s' % event

    def cb_3(self,event):
      print 'cb_3 - evt:%s' % event

  EVT_1 = 'One'
  EVT_2 = 'Two'
  EVT_3 = 'Three'
  EVT_4 = 'Four'
  lstEvents = [EVT_1,EVT_2,EVT_3, EVT_4]

  pbsb = PubSub()
  obj = TestPubSub()

  print pbsb
  for event in lstEvents:
    pbsb.publish(event)
  print

  pbsb.subscribe(EVT_1, obj.cb_1)
  print pbsb
  for event in lstEvents:
    pbsb.publish(event)
  print

  pbsb.subscribe(EVT_2, obj.cb_2)
  print pbsb
  for event in lstEvents:
    pbsb.publish(event)
  print

  pbsb.subscribeList([EVT_3,EVT_4], obj.cb_3)
  print pbsb
  for event in lstEvents:
    pbsb.publish(event)
  print

  pbsb.unsubscribe(EVT_1, obj.cb_1)
  print pbsb
  for event in lstEvents:
    pbsb.publish(event)
  print

  pbsb.unsubscribeList([EVT_3,EVT_4], obj.cb_3)
  print pbsb
  for event in lstEvents:
    pbsb.publish(event)
  print


