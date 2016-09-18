#!/usr/bin/env python
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

def getTo(stations):
    global collection
    response = collection.find({u"To": {u"$exists": u"True"}})

    for x in response:
        addStation(stations, x[u'To'])

    l = stations.items()
    sl = sorted(l, key=lambda l: l[1], reverse=True)

    return sl

def getFrom(stations):
    global collection
    response = collection.find({u"From": {u"$exists": u"True"}})

    for x in response:
        addStation(stations, x[u'From'])

    l = stations.items()
    sl = sorted(l, key=lambda l: l[1], reverse=True)

    return sl

def getPath(stations):
    global collection
    response = collection.find({u"path": {u"$exists": u"True"}})

    for x in response:
        for y in x[u'path']:
            addStation(stations, y)

    l = stations.items()
    sl = sorted(l, key=lambda l: l[1], reverse=True)

    return sl

def test_stations(sl, name):
    logger.info(u"{0} - {1} records" .format(name, len(sl)))
    for n in sl:
        logger.debug(u"{0!r} : {1!r}".format(n[0], n[1]))

def test_report():
    stations = dict()

    logger.debug(u"Check To")
    slTo = getTo(stations)
    test_stations(slTo, u"To")
    assert len(slTo) > 1

    logger.debug(u"Check From")
    slFrom = getFrom(stations)
    test_stations(slFrom, u"From")
    assert len(slFrom) > 1

    logger.debug(u"Check path")
    slPath = getPath(stations)
    test_stations(slPath, u"PATH")
    assert len(slPath) > 1

if __name__ == u"__main__":
    test_report()
