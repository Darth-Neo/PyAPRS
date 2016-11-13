#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = u"james.morris"

from geo_lib import *

from Logger import *
logger = setupLogging(__name__)
logger.setLevel(INFO)

def testDirection():
    for n, dn in enumerate(direction_names):
        angle = directions_step * n
        logger.info("%d : %s" % (angle, dn))

if __name__ == u"__main__":
    testDirection()
