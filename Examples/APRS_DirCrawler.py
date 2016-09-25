#!/usr/bin/env python
# __author__ = u"james.morris"
import os
from datetime import datetime
import sqlite3 as lite

from Logger import *

logger = setupLogging(u"APRS_DirCrawler")
logger.setLevel(DEBUG)


class APRSParser(object):

    def __init__(self, dbFile=None, subDir=None):

        if dbFile is None:
            self.dbFile = u"/home/james.morris/Documents/AFSK1200/afsk_1200.db"
        else:
            self.dbFile = dbFile

        if subDir is None:
            self.subdir = u"/home/james.morris/Documents/AFSK1200/saved"
        else:
            self.subDir = subDir

        self.conn = lite.connect(dbFile)

    def __del__(self):
        self.conn.close()

    def insertMessage(self, datetime, message1, message2):
        # hour, minute, tMessage = getTime()
        try:
            qs = u"insert into afsk1200_Decode (DateTime, message1, message2) values (?, ?, ?)"

            t = (datetime, message1, message2)

            logger.debug(u"%s" % qs)

            self.conn.execute(qs, t)

            self.conn.commit()

        except Exception, msg:
            logger.error(u"%s" % msg)

    def parseMessage1(self, msg):

        try:
            msgList = msg.split(u" ")

            msgTime = msgList[0]
            logger.debug(u"time: .%s." % msgTime)

            frmNode = msgList[2]
            logger.debug(u"from: .%s." % frmNode)

            toNode = msgList[4]
            logger.debug(u"  to: .%s." % toNode)

            viaNode = msgList[6]
            logger.debug(u" via: .%s." % viaNode)

            msgType = msgList[7]
            logger.debug(u"  mt: .%s." % msgType)

            pid = msgList[9]
            logger.debug(u" pid: .%s." % pid)

            t = (msgTime, frmNode, toNode, viaNode, msgType, pid)
            qs = u"insert into ParsedMessageOne (msgTime, frmNode, toNode, viaNode, msgType, pid) values (?, ?, ?, ?, ?, ?)"

            self.conn.execute(qs, t)

            self.conn.commit()

        except Exception, msg:
            logger.error(u"%s" % msg)

    def parseMessages(self):
        qs1 = u"select DateTime from afsk1200_Decode"
        qs2 = u"select message1 from afsk1200_Decode"

        cursor = self.conn.execute(qs2)

        for message1 in cursor.fetchall():
            logger.debug(u"%s" % message1[0])
            # parseDateTime(message1)

            try:
                self.parseMessage1(message1[0])

            except Exception, msg:
                logger.error(u"%s" % msg)

    def runQuery(self, query=None):
        if query is None:
            qs = u"select frmNode, count(*) from ParsedMessageOne  group by frmNode order by count(frmNode) desc;"
        else:
            qs = query

        cursor = self.conn.execute(qs)

        for frmNode, count in cursor.fetchall():
            logger.debug(u"%s - %d" % (frmNode, count))

    def execSQL(self, sql=None):
        if sql is None:
            qs = u"select DateTime, count(DateTime) from afsk1200_Decode group by DateTime"
        else:
            qs = sql

        cursor = self.conn.execute(qs)

        for dt, c in cursor.fetchall():
            print(u"%s %d" % (dt, c))

    def insertDateTime(self, datetime, message1, message2):

        try:

            DateTime = message1[:8]
            message1 = message1.strip(u"'").decode(u"utf8", errors=u"replace")
            message2 = message2.strip(u"'").decode(u"utf8", errors=u"replace")

            t = (datetime, message1, message2)

            qs = u"insert into afsk1200_Decode (DateTime, message1, message2) values (?, ?, ?)"

            logger.debug(u"%s" % qs)

            self.conn.execute(qs, t)
            self.conn.commit()

        except Exception, msg:
            logger.error(u"%s" % msg)

    def getMessages(self, nameFile):
        with open(nameFile, u"rb") as fo:
            lineMessages = fo.readlines()

        datetime = nameFile[-14:-4]
        n = 0

        try:
            while n < len(lineMessages):
                message1 = lineMessages[n].rstrip().lstrip()
                n += 1
                message2 = lineMessages[n].rstrip().lstrip()
                n += 1
                logger.info(u"%s\t%s" % (message1, message2))

                self.insertMessage(datetime, message1, message2)

        except Exception, msg:
            logger.error(u"%s" % msg)

    def searchSubDir(self, subdir):
        numFilesParsed = 0

        for root, dirs, files in os.walk(subdir, topdown=True):
            logger.debug(u"%s" % files)
            for name in files:
                nameFile = os.path.join(root, name)
                logger.debug(u"%s" % nameFile[-4:])
                if nameFile[-4:] == u".txt":
                    logger.info(u"%s" % nameFile)
                    self.getMessages(nameFile)

        return numFilesParsed

    @staticmethod
    def parseDateTime(self, msg):

        ml = len(msg)
        m = msg

        logger.debug(u"msg len[%d]" % ml)

        year = int(m[0:2])
        month = int(m[3:4])
        day = int(m[5:6])

        if ml == 10:
            hour = int(m[6:8])
            minute = int(m[9:10])
        else:
            hour = 0
            minute = 0

        logger.info(u"%d-%d-%d %d:%d" % (year, month, day, hour, minute))

    @staticmethod
    def getTime():

        dt = datetime.now().strftime(u"%I:%M")
        hour = int(dt.split(u":")[0])
        minute = int(dt.split(u":")[1])

        tMessage = (datetime.now().strftime(u"%I:%M %p"))

        return hour, minute, tMessage


if __name__ == u"__main__":
    subDir = u"/home/james.morris/Documents/AFSK1200/saved"
    dbFile = u"/home/james.morris/Documents/AFSK1200/afsk_1200.db"

    parser = APRSParser(dbFile, subDir)

    parser.searchSubDir()

    # parser.execSQL(conn, sql=None)
    # parser.parseMessages(conn)
    parser.runQuery()
