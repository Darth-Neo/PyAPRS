#!/usr/bin/env python
#
# Logging
#
__VERSION__ = 0.1
__author__ = u'morrj140'
import os
import logging
import logging.handlers

DEBUG = logging.DEBUG
INFO  = logging.INFO
WARN  = logging.WARN
ERROR = logging.ERROR


def setupLogging(name):
    #
    # Logging setup
    #
    logFile = u'./logs/aprs.log'
    ensure_dir(logFile)
    logger = logging.getLogger(name)

    # Note: Levels - DEBUG INFO WARN ERROR CRITICAL
    logger.setLevel(logging.INFO)

    logFormatter = logging.Formatter(u"%(asctime)s [%(levelname)-5.5s] [%(filename)s:%(lineno)s ] %(message)s")

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)

    fileHandler = logging.handlers.RotatingFileHandler(logFile, maxBytes=10485760, backupCount=0)
    fileHandler.setFormatter(logFormatter)
    logger.addHandler(fileHandler)

    return logger

def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)