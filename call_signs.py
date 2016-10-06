#!/usr/bin/env python
# #
# APRS Symbol Tables and Symbols
#
from Logger import *
logger = setupLogging(__name__)
logger.setLevel(INFO)

from pymongo import MongoClient


if __name__ == u"__main__":
    client = MongoClient(u'mongodb://localhost:27017/')
    db = client[u"local"]
    collection = db[u'Weather']

    url = u"http://aprs.fi/info/a/" + u"KJ4DXK-9"

    call_signs = list()

    for doc in collection.find({u"to": {u"$exists": u"True"}}):
        cs = list()
        cs.append(doc[u"to"])
        logger.info(u"{}".format(doc[u"to"]))

        cs.append(doc[u"from"])
        logger.info(u"    {}".format(doc[u"from"]))

        call_signs.append(cs)

    for doc in collection.find({u"To": {u"$exists": u"True"}}):
        cs = list()
        cs.append(doc[u"To"])
        logger.info(u"{}".format(doc[u"To"]))

        cs.append(doc[u"From"])
        logger.info(u"    {}".format(doc[u"From"]))
        call_signs.append(cs)

    pass





