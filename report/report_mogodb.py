#!/usr/bin/env python
from bson.code import Code
from pymongo import MongoClient

from Logger import *
logger = setupLogging(__name__)
logger.setLevel(INFO)

client = MongoClient(u'mongodb://localhost:27017/')
db = client[u'local']
collection = db[u'Weather']

def addStation(d, s):
    try:
        if s in d:
            d[s] += 1
        else:
            d[s] = 1
    except Exception, msg:
        logger.error(u"Error : %s" % msg)

def logResults(sl):
    for doc in sl:
        output = u""
        for k, v in doc.items():
            # output += u"{0} : {1}\t".format(k, v)
            output += u"%10s : %12s" % (k, v)
        logger.info(output)

def getTo():
    name = __name__
    global collection
    reducer = Code(u"""function(obj, prev){  prev.count++;} """)

    results = collection.group(key={u"To": 1}, condition={}, initial={u"count": 0}, reduce=reducer, finalize=None)
    sl = sorted(results, key=lambda result: result[u"count"], reverse=True)
    logger.info(u"{0} - {1} records".format(name, len(sl)))
    return sl

def getFrom():
    name = __name__
    global collection

    reducer = Code(u"""function(obj, prev){  prev.count++;} """)

    results = collection.group(key={u"From": 1}, condition={}, initial={u"count": 0}, reduce=reducer, finalize=None)
    sl = sorted(results, key=lambda result: result[u"count"], reverse=True)
    logger.info(u"{0} - {1} records".format(name, len(sl)))
    return sl

def getPath():
    name = __name__
    global collection

    reducer = Code(u"""function(obj, prev){  prev.count++;} """)

    results = collection.group(key={u"Path": 1}, condition={}, initial={u"count": 0}, reduce=reducer, finalize=None)
    sl = sorted(results, key=lambda result: result[u"count"], reverse=True)
    logger.info(u"{0} - {1} records".format(name, len(sl)))
    return sl

def test_stations(sl, name):
    logger.info(u"{0} - {1} records" .format(name, len(sl)))
    for n in sl:
        logger.debug(u"{0!r} : {1!r}".format(n[0], n[1]))

def test_report():

    if False:
        logger.debug(u"Check To")
        slTo = getTo()
        assert len(slTo) > 1
        logResults(slTo)

    if False:
        logger.debug(u"Check From")
        slFrom = getFrom()
        assert len(slFrom) > 1
        logResults(slFrom)

    if True:
        logger.debug(u"Check path")
        slPath = getPath()
        assert len(slPath) > 1
        logResults(slPath)

if __name__ == u"__main__":
    test_report()
