#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = u"james.morris"
import os
import sys, getopt
import time
import re
import aprslib
import hashlib
from datetime import datetime, timedelta
from subprocess import *
from dateutil import tz
from datetime import date, datetime
from rmq.rmq_send import *

from pymongo import *

from Logger import *
logger = setupLogging(__name__)
logger.setLevel(INFO)

field_errors = 0
field_count = 0
client = MongoClient(u'mongodb://localhost:27017/')
database = u"local"
collection = u"Weather"
CLEAR_DB = True # True
SLEEP_TIME = 10 # 5 minutes times 60 seconds

configFile=u"." + os.sep + u"rmq" + os.sep + u"rmq_settings.conf"
logger.info(u"%s" % configFile)
rbs = RabbitSend(configFile=configFile)
CLEAR_MESSAGES = True

def run_cmd(cmd):
    p = Popen(cmd, shell=True, stdout=PIPE)
    output = p.communicate()[0]
    return output

def get_CommandLine_Options(av):
    program = u""
    opts = u""
    inputfile = u""
    outputfile = u""

    try:
        program = os.path.basename(av[0])
        opts, args = getopt.getopt(av, u"hi:o:", [u"ifile=", u"ofile="])

    except getopt.GetoptError, m:
        logger.error(u"%s" % m)

    for opt, arg in opts:
        if opt == u'-h':
            logger.info(u"%s -i <inputfile> -o <outputfile>" % program)
            sys.exit()

        elif opt in (u"-i", u"--ifile"):
            inputfile = arg

        elif opt in (u"-o", u"--ofile"):
            outputfile = arg

    logger.debug(u"Input file is %s" % inputfile)
    logger.debug(u"'Output file is %s" % outputfile)

    return program, inputfile, outputfile

def get_gqrx_log_files(test=False):
    logs = list()
    path = os.environ[u"HOME"] + os.sep + u"logs"

    if test is True:
        rFile = u"test" + os.sep + u"test_messages.txt"
        logs.append(rFile)

    else:
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                rFile = os.path.join(root, name)
                logger.debug(u"%s" % rFile)

                if re.match(r"^gqrx-[0-9]+-[0-9]+-[0-9]+-[0-9]+-[0-9]+.log", name, re.M | re.I):
                    logs.append(rFile)

    return logs

def get_aprs_messages(messages):
    aprs_messages = list()
    begin_message = False

    bfr = messages.split(u"\n")
    for n, aprs_message in enumerate(bfr):

        if re.match(r"[ ]*[0-9]+:[0-9]+:[0-9]+.*", aprs_message, re.M | re.I):
            logger.debug(u"%3d PF    : %s " % (n, aprs_message))
            begin_message = True

        elif re.match(r"^AFSK1200:.*", aprs_message, re.M | re.I):
            logger.debug(u"%3d PF    : %s " % (n, aprs_message))
            begin_message = True

        elif begin_message is True:
            logger.debug(u"%3d PD    : %s " % (n, aprs_message))
            m = list()
            m.append(bfr[n - 1].lstrip())
            m.append(bfr[n].lstrip())
            aprs_messages.append(m)
            begin_message = False

    return aprs_messages

def display_Message(message):
    global rbs

    if u"to" in message:
        rbs.send_message(u"From: {0}\nTo:   {1}".format(message[u"From"], message[u"To"]))
    elif u"To" in message:
        rbs.send_message(u"From: {0}\nTo:   {1}".format(message[u"From"], message[u"To"]))

    gm = [u"Temperature", u"Humidity", u"Barometer", ]
    for k, v in message.items():
        logger.info(u"{0} : {1}".format(k, v))
        if k in gm:
            if v is not None:
                logger.info(u"*** Match : {0} ***".format(v))
                rbs.send_message(u"{0}\n{1}".format(k, v))

    dtt = datetime.now().strftime(u"%b %d %Y\n%I:%M %p")
    rbs.send_message(dtt)

def insert_Message(message, header=None, footer=None, hash=False):
    global client
    global CLEAR_DB
    global database
    global collection

    display_Message(message)

    db = client[database]
    c = db[collection]

    if CLEAR_DB is True:
        logger.info(u"Reset MongoDB")
        c.remove()
        CLEAR_DB = False

    if message is None:
        return None

    try:
        if header is not None and footer is not None:

            message[u"Header"] = header
            message[u"Footer"] = footer
            message[u"ReadingDateTime"] = u"%s" % datetime.now()

            if hash is True:
                msg = dict()
                hs = header + footer
                ho = hashlib.sha512(hs)
                message[u"Hash"] = u"%s" % ho.digest().decode(u"utf8", errors=u"replace")
                message.update(msg)

    except Exception, msg:
        logger.warn(u"%s" % msg)

    c.insert_one(message)


def log_aprs_lib_message(result):
    """
    Logs eMic messages that have special decoding needs
    :param result:
    :return:
    """

    for n, emix in enumerate(result):
        try:
            part = result[emix]
            if isinstance(part, (str, unicode)):
                logger.debug(u"       %s : %s" % (emix, part))
            elif isinstance(part, int):
                logger.debug(u"       %s : %3d" % (emix, part))
            elif isinstance(part, float):
                logger.debug(u"       %s : %3.3f" % (emix, part))
            else:
                logger.debug(u"       %s : tbd" % emix)
        except Exception, msg:
            logger.error(u"%s" % msg)


def parse_ULTW_Message(field, msg, scale=1.0):
    u"""
    function to convert hex to the proper value
    :param field:
    :param msg:
    :param scale:
    :return:
    """
    fld = None
    try:
        #if field <> u"----":
        if re.match(r"^[0-9A-Za-z]{4}", field, re.M | re.I):
            fld = int(u"0x" + field, 16) * scale
            logger.debug(u"%7.2f : %s" % (fld, msg))
    except Exception, msg:
        logger.warn(u"%s : %s" % (msg, field))

    return fld


def parse_Zulu_EDT(pt):

    try:
        if True:
            t = int(u"0x" + pt, 16)
        else:
            t = int(pt)

        hours = t / 60
        minutes = t % 60

        zulu = u"%2d:%2d" % (hours, minutes)

    except Exception, msg:
        logger.warn(u"%s" % msg)
        return pt

    return zulu


def parse_Days(days):
    year = int(datetime.now().strftime(u'%Y'))
    n = datetime(day=1, month=1, year=year)
    EndDate = n + timedelta(days=days)

    return EndDate.strftime(u'%Y/%m/%d')


def parse_aprs_fields(fields):
    """
    Create a dict of decoded fields
    :param fields:
    :return:
    """
    weather = [u"@", u"=", u"_", u"/", u"!"]
    fld = dict()
    global field_errors
    global field_count

    # Weather Messages
    if fields[0] in weather:
        fld[u"Message_Type"] = fields[0]
        field_count += len(fields)
        for n, field in enumerate(fields[1:]):
            # logger.debug(u"%03d : %s" % (n, field))

            try:
                if field[0] == u"t":
                    n = 1
                    logger.info(u"%6d : [ Temperature ]" % int(field[1:]))
                    fld[u"Temperature"] = int(field[1:])
                elif field[0] == u"h":
                    n = 2
                    logger.info(u"%6d : [ Humidity ]" % int(field[1:]))
                    fld[u"Humidity"] = int(field[1:])

                elif field[0] == u"r":
                    n = 4
                    if len(field[1:]) > 2:
                        fv = int(field[1:]) * 0.01
                        logger.info(u"%6.1f : [ Rainfall in the last hour ]" % fv)
                        fld[u"Rainfall in the last hour"] = fv
                elif field[0] == u"P":
                    n = 5
                    fv = int(field[1:]) * 0.01
                    logger.info(u"%6.1f : [ Rainfall in the last 24 hour]" % fv)
                    fld[u"Rainfall in the last 24 hour"] = fv
                elif field[0] == u"p":
                    n = 6
                    fv = int(field[1:]) * 0.01
                    logger.info(u"%6.1f : [ Rainfall since midnight ]" % fv)
                    fld[u"Rainfall since midnight"] = fv

                elif field[0] == u"b":
                    n = 7
                    fv = float(field[1:]) * 0.1
                    logger.info(u"%6.1f : [ Barometric Pressure] " % fv)
                    # fld[u"Barometric Pressure"] = fv
                    fld[u"Barometer"] = fv

                elif field[0] == u"c":
                    n = 8
                    fv = int(field[1:])
                    logger.debug(u"%6d : [ Wind Direction ]" % fv)
                    fld[u"Wind Direction"] = fv
                elif field[0] == u"s":
                    n = 9
                    fv = int(field[1:])
                    logger.info(u"%6d : [ Sustained Wind Speed ]" % fv)
                    fld[u"Sustained wind speed"] = fv
                elif field[0] == u"g":
                    n = 10
                    fv = int(field[1:])
                    logger.info(u"%6d : [ Wind Gust]" % fv)
                    fld[u"Wind Gust"] = fv

                elif field[-1:] in (u"N", u"S"): #  and len(field) > 2:
                    n = 11
                    logger.debug(u"%6s : [ Latitude ]" % field)
                    fld[u"Latitude"] = field
                elif field[-1:] in (u"E", u"W"):
                    n = 12
                    logger.debug(u"%6s : [ Longitude ]" % field)
                    fld[u"Longitude"] = field

                elif field[-1:] in (u"z",):
                    n = 14
                    zt = u"%s:%s:%s" % (field[:2], field[2:4], field[4:6])
                    fld[u"Zulu Time"] = zt

                elif field[0] in (u"\\", u"/",):
                    n = 15
                    logger.debug(u"%6s : [ Alternate Symbol Table ]" % field[0])
                    fld[u"Alternate Symbol Table"] = field[0]
                elif field[0] in (u"v",):
                    n = 16
                    logger.debug(u"%6s : [ Vehicle ] " % field[0])
                    fld[u"Vehicle"] = field[0]

                elif field[3] in (u"/",):
                    n = 17
                    logger.debug(u"%6s : [ Course/Speed ] " % field[0])
                    fld[u"Course/Speed"] = field[0]
                else:
                    n = 18
                    logger.debug(u"%6s : [ TBD ]" % field)
                    fld[u"TBD"] = field[0]

            except Exception, msg:
                logger.debug(u"%s[%d] : %s " % (field, n, msg))
                field_errors += 1
        return fld

    # ULTW Messages
    elif fields[0][:5] == u"$ULTW":
        # $ULTW 0000 0000 01FF 0004 27C7 0002 CCD3 0001 026E 003A 050F 0004 0000
        fld[u"Message_Type"] = u"ULTW"
        field_count += len(fields)

        try:
            n = 20
            m = u"Wind Speed Peak over last 5 min (0_1 kph increments)"
            msg = u"Wind Speed PeaK"
            fld[msg] = parse_ULTW_Message(fields[1], msg, scale=0.1)

            n = 21
            m = u"Wind Direction of Wind Speed Peak (0-255)"
            msg = u"Wind Direction"
            fld[msg] = parse_ULTW_Message(fields[2], msg)

            n = 22
            m = u"Current Outdoor Temp (0_1 deg F increments)"
            msg =u"Temperature"
            fld[msg] = parse_ULTW_Message(fields[3], msg, scale=0.1)

            n = 23
            msg = u"Rain Long Term Total (0_01 in increments)"
            #fld[msg] = parse_ULTW_Message(fields[4], msg, scale=0.01)

            n = 24
            m = u"Current Barometer (0_1 mbar increments)"
            msg = u"Barometer"
            fld[msg] = parse_ULTW_Message(fields[5], msg, scale=0.1)

            n = 25
            # m = u"Barometer Delta Value(0_1 mbar increments)"
            # msg = u"Barometer Delta"
            # fld[msg] = parse_ULTW_Message(fields[6], msg, scale=0.1)

            n = 26
            # msg = u"Barometer Corr Factor(LSW)"
            # fld[msg] = parse_ULTW_Message(fields[7], msg)

            n = 27
            # msg = u"Barometer Corr Factor(MSW)"
            # fld[msg] = parse_ULTW_Message(fields[8], msg)

            n = 28
            m = u"Current Outdoor Humidity (0_1 increments)"
            msg = u"Humidity"
            fld[msg] = parse_ULTW_Message(fields[9], msg, scale=0.1)

            n = 29
            m = u"Date (day of year since January 1)"
            msg = u"Date"
            #fld[msg] = parse_ULTW_Message(fields[10], msg)

            n = 30
            msg2 = u"Zulu Time"
            pzt = parse_Zulu_EDT(fields[11])
            fld[msg2] = pzt
            m = u"Time (minute of day)"
            msg = u"Time"
            fld[msg] = parse_ULTW_Message(fields[11], msg)

            n = 31
            msg = u"Today's Rain Total (0_01 inch increments)"
            #fld[msg] = parse_ULTW_Message(fields[12], msg, scale=0.01)

            n = 32
            msg = u"Minute Wind Speed Average (0_1kph increments)"
            #fld[msg] = parse_ULTW_Message(fields[13], msg, scale=0.1)

            field_count += len(fld)

            return fld

        except KeyError, msg:
            logger.debug(u"$ULTW[%d] Error : %s" % (n, msg))
            field_errors += 1

    # Unknown Message
    else:
        logger.debug(u"Unknown")
        return None


def parse_aprs_header(header, footer, n=0):
    header_fields = None
    aprs_addresses = None

    try:
        # fm WC4PEM-10 to APMI06-0 via WC4PEM-14,WIDE2-1 UI  pid=F0
        addresses = header.split(u" ")
        fm = addresses[2]
        to = addresses[4]
        path = addresses[6]

        if path is None or not(len(path) > 1):
            via = addresses[5]
            logger.error(u"via is {0!r}".format(via))

        # M0XER-4>APRS64,TF3RPF,WIDE2*,qAR,TF3SUT-2
        aprs_addresses = u"{0}>{1},{2}:{3}" .format(fm, to, path, footer)
        message = u"{0!r} ->{1!r}-> {2!r}".format(fm, path, to)
        logger.info(message)

        logger.debug(u"%3d [%s]" % (n, header[10:]))
        logger.debug(u"    [%s]" % footer)

        header_fields = {u"From" : fm, u"To" : to, u"Path": path}
    except Exception, msg:
        logger.error(u"%s" % msg)

    return header_fields, aprs_addresses


def parse_aprs_footer(footer, msg_bytes):
    n = y = x = 0
    fields = list()
    logger.debug(u"%s" % footer)
    ml = len(footer)

    try:
        while True:
            y += msg_bytes[n]
            logger.debug(u"%d : %d" % (x, y))
            if msg_bytes[n] == 0:
                field = footer[x:]
                fields.append(field)
                break
            else:
                field = footer[x:y]
                fields.append(field)
            # logger.debug(u"Field %d : %s" % (n, field))
            x = y
            n += 1
            if x >= ml:
                break

    except Exception, em:
        logger.error(u"%s - %s[%d:%d]" % (em, footer, x, y))

    fields = parse_aprs_fields(fields)

    return fields


def decode_aprs_messages(msgs):

    global field_errors
    mt = dict()

    for n, message in enumerate(msgs):

        try:
            header = message[0].lstrip()
            footer = message[1].lstrip()

            header_fields, aprs_addresses = parse_aprs_header(header, footer, n=n)

            logger.debug(u"%3d [%s]" % (n, header[10:]))
            logger.debug(u"    [%s]" % footer)

            # Message Counter
            if footer[0] in mt:
                mt[footer[0]] += 1
            else:
                mt[footer[0]] = 1

            if re.match(r"^ *[0-9]+:[0-9]+:[0-9]+.*", header, re.M | re.I):
                logger.debug(u"1 H.%3d PF    : %s " % (n, header))

                if False:
                    m = header.split(u" ")
                    for x in m:
                        logger.debug(u"H.%3d.%s" % (n, x))

            # 1
            if re.match(r"^\$ULTW.*", footer, re.M | re.I):
                # # __________________________________________________________________________________
                # $ indicates a Ultimeter 2000
                # $ULTW 0000 0000 01FF 0004 27C7 0002 CCD3 0001 026E 003A 050F 0004 0000
                u"""
                Field #1,  0000 = Wind Speed Peak over last 5 min. ( reported as 0.1 kph increments)
                Field #2,  0000 = Wind Direction of Wind Speed Peak (0-255)
                Field #3,  01FF = Current Outdoor Temp (reported as 0.1 deg F increments)
                Field #4,  0004 = Rain Long Term Total (reported in 0.01 in. increments)
                Field #5,  27C7 = Current Barometer (reported in 0.1 mbar increments)
                Field #6,  0002 = Barometer Delta Value(reported in 0.1 mbar increments)
                Field #7,  CCD3 = Barometer Corr. Factor(LSW)
                Field #8,  0001 = Barometer Corr. Factor(MSW)
                Field #9,  026E = Current Outdoor Humidity (reported in 0.1% increments)
                Field #10, 003A = Date (day of year since January 1)
                Field #11, 050F = Time (minute of day)
                Field #12, 0004 = Today's Rain Total (reported as 0.01 inch increments)
                Field #13, 0000 = 1 Minute Wind Speed Average (reported in 0.1kph increments)
                """
                try:
                    logger.info(u"1 Ultimeter 2000")
                    message_bytes = (5, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 0)
                    fields = parse_aprs_footer(footer, message_bytes)
                    fields.update(header_fields)
                    insert_Message(fields, header=header, footer=footer)
                except Exception, msg:
                    logger.warn(u"1 %s" % msg)

            # 2 - aprslib !
            elif re.match(r"^!.*", footer, re.M | re.I):
                # __________________________________________________________________________________
                # Raw Weather Report - Ultimeter
                # !2749.10N S 08215.39W # PHG56304/W3,FLn Riverview, FL www.ni4ce.org (wind @ 810ft AGL)
                # !         Message
                # 2749.10N  Latitude
                # S         Symbol Table ID
                # 08215.39W Longitude
                # #
                # PHG56304/W3,FLn Riverview, FL www.ni4ce.org (wind @ 810ft AGL)
                try:
                    logger.info(u"2a Raw Weather Report")
                    fields = aprslib.parse(aprs_addresses)
                    log_aprs_lib_message(fields)
                    insert_Message(fields, header=header, footer=footer)

                except Exception, msg:
                    logger.debug(u"2 %s" % msg)
                    logger.debug(u"2b Raw Weather Report")
                    message_bytes = (1, 8, 1, 9, 1, 0)
                    fields = parse_aprs_footer(footer, message_bytes)
                    fields.update(header_fields)
                    insert_Message(fields, header=header, footer=footer)

            # 3 _
            elif re.match(r"^_.*", footer, re.M | re.I):
                # __________________________________________________________________________________
                # Positionless Weather Report Positionless Weather Data
                # _ 0731 1701 c189 s004 g006 t094 r000 p000 P000 h00 b1016 5wDAV
                # _ Message
                # 0731 Month Day
                # 1701 Time
                # c189 Wind Direction
                # s004 Wind Speed
                # g006 Wind Gust in the last five minutes
                # t094 Temperature
                # r000 Rainfall in the last hour
                # p000 Rainfall in the last 24 hours
                # P000 Rainfall since midnight
                # h00  Humidity
                # b1016 Barometric Pressure
                # 5     APRS Software
                # wDAV  WX Unit -  WinAPRS
                try:
                    logger.info(u"3a Raw Weather Report")
                    fields = aprslib.parse(aprs_addresses)
                    log_aprs_lib_message(fields)
                    insert_Message(fields, header=header, footer=footer)

                except Exception, msg:
                    try:
                        # MDHM
                        logger.debug(u"3b Positionless Weather Report")
                        message_bytes = (1, 4, 4, 4, 4, 4, 4, 4, 4, 4, 3, 6, 1, 3, 0)
                        fields = parse_aprs_footer(footer, message_bytes)
                        fields.update(header_fields)
                        insert_Message(fields, header=header, footer=footer)

                    except Exception, msg:
                        logger.debug(u"3c Positionless Weather Report")
                        message_bytes = (1, 4, 4, 4, 4, 4, 4, 4, 4, 4, 3, 5, 1, 4, 0)
                        fields = parse_aprs_footer(footer, message_bytes)
                        fields.update(header_fields)
                        insert_Message(fields, header=header, footer=footer)

            # 4 aprslib =
            elif re.match(r"^=.*", footer, re.M | re.I):
                # __________________________________________________________________________________
                # Complete Weather Report Format - with Lat/Log position, no Timestamp
                # =2835.63NS08118.08W#PHG8250/DIGI_NED: OCCA Digi,www.w4mco.org,N2KIQ@arrl.net
                # =           Message
                # 2835.63N    Latitude
                # S           Symbol Table ID
                # 08118.08W   Longitude
                # #PHG8250/DIGI_NED: OCCA Digi,www.w4mco.org,N2KIQ@arrl.net

                try:
                    logger.info(u"4 Complete Weather Report")
                    fields = aprslib.parse(aprs_addresses)
                    log_aprs_lib_message(fields)
                    insert_Message(fields, header=header, footer=footer)

                except Exception, msg:
                    logger.warn(u"4 %s" % msg)
                    try:
                        logger.debug(u"4a Complete Weather Report")
                        message_bytes = (1, 8, 1, 9, 0)
                        fields = parse_aprs_footer(footer, message_bytes)
                        fields.update(header_fields)
                        insert_Message(fields, header=header, footer=footer)

                    except Exception, msg:
                        logger.warn(u"4 %s" % msg)
                        logger.debug(u"4b Complete Weather Report")
                        message_bytes = (1, 1, 4, 4, 1, 2, 1, 4, 4, 4, 4, 4, 4, 3, 6, 0)
                        fields = parse_aprs_footer(footer, message_bytes)
                        fields.update(header_fields)
                        insert_Message(fields, header=header, footer=footer)

            # 5 aprslib @
            elif re.match(r"^@.*", footer, re.M | re.I):
                # __________________________________________________________________________________
                # Complete Weather Format
                # @220605z2831.07N/08142.92W_000/000g002t100r000p000P000h46b10144.DsVP
                # @ 220605z 2831.07N / 08142.92W _000/000 g002 t100 r000 p000 P000 h46 b10144 .DsVP.
                # @ Message
                # 22 06 05z Zulu Time
                #  2831.07N Latitude
                # 08142.92W Longitude
                # g002      Wind Gust in the last five minutes
                # t100      Temperature
                # r000      Rainfall in the last hour
                # p000      Rainfall in the last 24 hours
                # P000      Rainfall since midnight
                # h46       Humidity
                # b10144    Barometric Pressure
                try:
                    logger.info(u"5 Complete Weather Format")
                    fields = aprslib.parse(aprs_addresses)
                    log_aprs_lib_message(fields)
                    insert_Message(fields, header=header, footer=footer)

                except Exception, msg:
                    try:
                        logger.debug(u"5b Complete Weather Format")
                        message_bytes = (1, 7, 8, 1, 9, 1, 7, 4, 4, 4, 4, 4, 3, 6, 0)
                        fields = parse_aprs_footer(footer, message_bytes)
                        fields.update(header_fields)
                        insert_Message(fields, header=header, footer=footer)

                    except Exception, msg:
                        logger.debug(u"5c Complete Weather Format")
                        message_bytes = (1, 7, 8, 1, 9, 4, 4, 4, 4, 4, 4, 3, 6, 0)
                        fields = parse_aprs_footer(footer, message_bytes)
                        fields.update(header_fields)
                        insert_Message(fields, header=header, footer=footer)

            # 6 aprslib /
            elif re.match(r"^/.*", footer, re.M | re.I):
                # __________________________________________________________________________________
                # Complete Weather Report Format — with Compressed Lat/Long position, with Timestamp
                # / 311704z 2 757.15N / 08147.20W _ 103/008 g012 t094 r000 p001 P000 h41 b1018 3
                # / Message
                # 31 17 04z  Zulu Time DHM
                # 2757.15N   Latitude
                # /          Symbol Table ID
                # 08147.20W  Longitude
                # _          Symbol Code
                # 103/008    Wind Speed and Direction
                # g012       Wind Gust in the last five minutes
                # t094       Temperature
                # r000       Rainfall in the last hour
                # p001       Rainfall in the last 24 hours
                # P000       Rainfall since midnight
                # h41        Humidity
                # b10183     Barometric Pressure
                try:
                    logger.info(u"6 Complete Weather Report Format ")
                    fields = aprslib.parse(aprs_addresses)
                    log_aprs_lib_message(fields)
                    insert_Message(fields, header=header, footer=footer)

                except Exception, msg:
                    logger.debug(u"5 %s" % msg)
                    try:
                        logger.debug(u"6 Complete Weather Report Format ")
                        message_bytes = (1, 7, 8, 1, 9, 1, 7, 4, 4, 4, 4, 4, 3, 6, 1, 0)
                        fields = parse_aprs_footer(footer, message_bytes)
                        fields.update(header_fields)
                        insert_Message(fields, header=header, footer=footer)

                    except Exception, msg:
                        logger.debug(u"6 Trying alternate parsing : %s" % msg)

            # 7 aprslib ;
            elif re.match(r"^;.*", footer, re.M | re.I):
                # __________________________________________________________________________________
                # ;145.650  *051916z2749.31N/08244.16Wr/A=000025AA/Cert-Node 273835
                # ;
                # Object Name                           145.650
                # skip                                  *
                # Time DHM or HMS                       051916z
                # Lat                                   2749.31N
                # Symbol Table ID                       /
                # Long                                  08244.16Wr
                # Symbol Code                           /
                # Course Speed, Power/Height/Gain/Dir   A=00002
                # Comment                               5AA/Cert-Node 273835

                try:
                    logger.info(u"7a Object Report Format")
                    fields = aprslib.parse(aprs_addresses)
                    log_aprs_lib_message(fields)
                    insert_Message(fields, header=header, footer=footer)

                except Exception, msg:
                    logger.info(u"7b Object Report Format")

                    try:
                        message_bytes = (1, 9, 1, 7, 8, 1, 9, 1, 7, 0)
                        fields = parse_aprs_footer(footer, message_bytes)
                        fields.update(header_fields)
                        insert_Message(fields, header=header, footer=footer)

                    except Exception, msg: #else:
                        logger.info(u"7c %s" % msg)
                        message_bytes = (1, 9, 1, 7, 13, 43)
                        fields = parse_aprs_footer(footer, message_bytes)
                        fields.update(header_fields)
                        insert_Message(fields, header=header, footer=footer)

            # 8 aprslib >
            elif re.match(r"^>.*", footer, re.M | re.I):
                #
                # >- aprsfl.net/weather - New Port Richey WX
                try:
                    logger.debug(u"8 Unknown")
                    fields = aprslib.parse(aprs_addresses)
                    log_aprs_lib_message(fields)
                    insert_Message(fields, header=header, footer=footer)

                except Exception, msg:
                    logger.error(u"8 %s" % msg)

            # 9 aprslib :
            elif re.match(r"^:.*", footer, re.M | re.I):
                # __________________________________________________________________________________
                # :
                logger.info(u"9 Object Report Format")

                try:
                    fields = aprslib.parse(aprs_addresses)
                    log_aprs_lib_message(fields)
                    insert_Message(fields, header=header, footer=footer)
                except Exception, msg:
                    logger.warn(u"9 %s" % msg)
                    message_bytes = (1, 9, 1, 67, 1, 0)
                    fields = parse_aprs_footer(footer, message_bytes)
                    fields.update(header_fields)
                    insert_Message(fields, header=header, footer=footer)

            # 10 aprslib `
            elif re.match(r"^`.*", footer, re.M | re.I):
                # __________________________________________________________________________________
                # MicE Format
                # `
                logger.debug(u"10 eMic Format")
                fields = aprslib.parse(aprs_addresses)
                log_aprs_lib_message(fields)
                insert_Message(fields, header=header, footer=footer)

            else:
                # __________________________________________________________________________________
                logger.debug(u"No match - %s" % footer)


        except Exception, msg:
            logger.error(u"decodeMesssage : %s" % msg)
            field_errors += 1
            continue

    return mt


def decodeMessages(test=True):

    try:
        logFl = get_gqrx_log_files(test=test)

        for lf in logFl:
            logger.info(u"Reading : %s" % lf)
            with open(lf, "rb") as f:
                messages = f.read()

            msgs = get_aprs_messages(messages)
            mt = decode_aprs_messages(msgs)

            mtt = mt.items()
            mts = sorted(mtt, key=lambda mn: mn[1], reverse=True)

            mc = len(msgs)
            pf = float(field_errors) / float(field_count) * 100.0
            logger.info(u"Message Type Counts :  %4d " % mc)
            logger.info(u"Field Count         :  %4d " % field_errors)
            logger.info(u"Field Errors[%d]    : %3.2f%%" % (field_errors, pf))

            output = u"Top Ten : "
            for key, value in mts[:10]:
                output += u"%s[%s] " % (key, value)

            logger.info(u"%s" % output)

    except KeyboardInterrupt:
        logger.info(u"Bye ")


def loopDecodeMessages(test=True):
    eofl = dict()

    logFl = get_gqrx_log_files(test=test)

    while True:
        try:
            for n, lf in enumerate(logFl):

                if lf not in eofl.keys():
                    f = open(lf, "rb")
                    messages = f.read()
                    eofl[lf] = (f.tell(), f, lf)
                    logger.debug(u"%d : %s" % (f.tell(), lf))
                else:
                    eofm = eofl[lf][0]
                    f = eofl[lf][1]
                    f.seek(eofm)
                    messages = f.read()
                    eofl[lf] = (f.tell(), f, lf)
                    logger.debug(u"%d : %s" % (f.tell(), lf))

                msgs = get_aprs_messages(messages)
                decode_aprs_messages(msgs)

            time.sleep(SLEEP_TIME)

        except KeyboardInterrupt:
            logger.info(u"Bye ")


def test_decodeMessages():
    decodeMessages(test=True)

if __name__ == u"__main__":

    program, ifile, ofile = get_CommandLine_Options(sys.argv)



    if False:
        decodeMessages(test=False)
    else:
        loopDecodeMessages(test=False)