#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
from subprocess import *
from time import sleep, strftime
from datetime import datetime
import sqlite3 as lite


def execSQL(conn, sql):
    qs = u"select  DateTime, count(DateTime) from afsk1200_Decode group by DateTime"
    cursor = conn.execute(qs)

    conn.commit()


def getTime():
    dt = datetime.now().strftime(u"%I:%M")
    hour = int(dt.split(u":")[0])
    minute = int(dt.split(u":")[1])
    tMessage = (datetime.now().strftime(u"%I:%M %p"))
    return hour, minute, tMessage


def insertMessage(conn):
    hour, minute, tMessage = getTime()
    message1 = u".."
    message2 = u".."

    qs = u"insert into afsk1200_Decode (DateTime, message1, message2) \
         values ('%s', '%s', '%s') % (tMessage, message1, humidity)"

    print(u"%s" % qs)

    cursor = conn.execute(qs)

    conn.commit()


def getColumns(conn, name):
    qs = u"PRAGMA table_info(%s);" % name

    print(u"%s" % qs)

    cursor = conn.execute(qs)
    for x in cursor.fetchall():
        print(u"\t%s" % str(x))


def determineTables(conn):
    print(u"Tables...")

    # Determine Table Names
    cursor = conn.cursor()
    cursor.execute(u"SELECT name FROM sqlite_master WHERE type='table';")
    for x in cursor.fetchall():
        print(u"%s" % x)
        getColumns(conn, x)

if __name__ == u"__main__":
    conn = None
    dbFile = u"/home/james.morris/Documents/AFSK1200/afsk_1200.db"

    try:
        with lite.connect(dbFile) as conn:

            cur = conn.cursor()
            cur.execute(u"SELECT SQLITE_VERSION()")

            data = cur.fetchone()

            print(u"SQLite version: %s" % data)

            determineTables(conn)

    except lite.Error, e:

        print(u"Error %s:" % e.args[0])



