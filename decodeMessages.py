#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = u"james.morris"
import os
import sys, getopt
import time
import re
import aprslib

from Logger import *
logger = setupLogging(__name__)
logger.setLevel(INFO)


def convertULTW(field, msg, scale=1.0):
    if field <> u"----":
        fld = int(u"0x" + field, 16) * scale
        logger.info(u"%7.2f : %s" % (fld, msg))

def printFields(fields):
    weather = [u"@", u"=", u"_", u"/", u"!"]

    if fields[0] in weather:
        for n, field in enumerate(fields[1:]):
            logger.debug(u"%03d : %s" % (n, field))

            try:
                if field[0] == u"t":
                    logger.info(u"  Temperature                    : %d" % int(field[1:]))
                elif field[0] == u"h":
                    logger.info(u"  Humidity                       : %d" % int(field[1:]))

                elif field[0] == u"r":
                    fv = int(field[1:]) * 0.01
                    logger.info(u"  Rainfall in the last hour      : %2.1f" % fv)
                elif field[0] == u"P":
                    fv = int(field[1:]) * 0.01
                    logger.info(u"  Rainfall in the last 24 hour   : %2.1f" % fv)
                elif field[0] == u"p":
                    fv = int(field[1:]) * 0.01
                    logger.info(u"  Rainfall since midnight        : %2.1f" % fv)

                elif field[0] == u"b":
                    logger.info(u"  barometric pressure            : %5.1f" % (float(field[1:]) * 0.1))

                elif field[0] == u"c":
                    logger.info(u"  Wind Direction                 : %d" % int(field[1:]))
                elif field[0] == u"s":
                    logger.info(u"  Sustained wind speed           : %s" % int(field[1:]))
                elif field[0] == u"g":
                    logger.info(u"  Wind Gust                      : %d" % int(field[1:]))

                elif field[-1:] in (u"N", u"S") and len(field) > 2:
                    logger.info(u"  Latitude                       : %s" % field)
                elif field[-1:] in (u"E", u"W"):
                    logger.info(u"  Longitude                      : %s" % field)

                elif field[-1:] in (u"z",):
                    logger.info(u"  Zulu Time:                       %s:%s:%s" % (field[:2], field[2:4], field[4:6]))

                elif field[0] in (u"\\", u"/", ):
                    logger.info(u"  Alternate Symbol Table         : %s" % field[0])
                elif field[0] in (u"v", ):
                    logger.info(u"  Vehicle                        : %s" % field[0])

                elif field[3] in (u"/",):
                    logger.info(u"  Course/Speed                   : %s" % field[0])
                else:
                    logger.info(u"  TBD                            : %s" % field)


            except Exception, msg:
                logger.debug(u"%s " % msg)

    elif fields[0] in [u":"]:
        for field in fields:
            if field[-1:] in (u"N", u"S", u"E", u"W"):
                logger.info(u"LAT/LOG : %s" % field)

    elif fields[0][:5] == u"$ULTW":
        # $ULTW 0000 0000 01FF 0004 27C7 0002 CCD3 0001 026E 003A 050F 0004 0000

        try:

            msg = u"[1. Wind Speed Peak over last 5 min. (0.1 kph increments)]"
            convertULTW(fields[1], msg, scale=0.1)

            msg = u"[2. Wind Direction of Wind Speed Peak (0-255)]"
            convertULTW(fields[2], msg)

            msg = u"[3. Current Outdoor Temp (0.1 deg F increments)"
            convertULTW(fields[3], msg, scale=0.1)

            msg = u"[4. Rain Long Term Total (0.01 in. increments)]"
            convertULTW(fields[4], msg, scale=0.01)

            msg = u"[5. Current Barometer (0.1 mbar increments)"
            convertULTW(fields[5], msg, scale=0.1)

            # msg = u"[6. Barometer Delta Value(0.1 mbar increments)]"
            # convertULTW(fields[6], msg, scale=0.1)

            # msg = u"[7. Barometer Corr. Factor(LSW)]"
            # convertULTW(fields[7], msg)

            # msg = u"[8. Barometer Corr. Factor(MSW)]"
            # convertULTW(fields[8], msg)

            msg = u"[9. Current Outdoor Humidity (0.1 increments)]"
            convertULTW(fields[9], msg, scale=0.1)

            msg = u"[10. Date (day of year since January 1) ]"
            convertULTW(fields[10], msg)

            msg = u"[11. Time (minute of day)]"
            convertULTW(fields[11], msg)

            msg = u"[12. Today's Rain Total (0.01 inch increments)]"
            convertULTW(fields[12], msg, scale=0.01)

            msg = u"[13. Minute Wind Speed Average (0.1kph increments)]"
            convertULTW(fields[13], msg, scale=0.1)

        except KeyError, msg:
            logger.warn(u"$ULTW Error : %s" % msg)

    else:
        logger.debug(u"Unknown")

    if fields[0] == u"_":
        fld = fields[len(fields) - 1]
        fl1 = fld[:1]
        fl2 = fld[1:3]
        logger.info(u"  %s : %s " % (fl1, fl2))


def parseMessage(msg, msg_bytes):
    n = y = x = 0
    fields = list()
    logger.debug(u"%s" % msg)
    ml = len(msg)

    try:
        while True:
            y += msg_bytes[n]
            logger.debug(u"%d : %d" % (x, y))
            if msg_bytes[n] == 0:
                field = msg[x:]
                fields.append(field)
                break
            else:
                field = msg[x:y]
                fields.append(field)
            logger.debug(u"Field %d : %s" % (n, field))
            x = y
            n += 1
            if x >= ml:
                break

    except Exception, em:
        logger.error(u"%s - %s[%d:%d]" % (em, msg, x, y))

    printFields(fields)

    return fields


def get_GQRX_Output():
    logs = list()
    path = os.environ[u"HOME"] + os.sep + u"logs"

    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            rFile = os.path.join(root, name)
            logger.debug(u"%s" % rFile)

            if re.match(r"^gqrx-[0-9]+-[0-9]+-[0-9]+-[0-9]+-[0-9]+.log", name, re.M | re.I):
                logs.append(rFile)

    return logs


def getMessages(messages):
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


def decodeMessages(msgs):
    for n, message in enumerate(msgs):

        header = message[0].lstrip()
        footer = message[1].lstrip()

        logger.info(u"%3d [%s]" % (n, header[10:]))
        logger.info(u"    [%s]" % footer)

        if re.match(r"^ *[0-9]+:[0-9]+:[0-9]+.*", header, re.M | re.I):
            logger.debug(u"1 H.%3d PF    : %s " % (n, header))

            if False:
                m = header.split(u" ")
                for x in m:
                    logger.info(u"H.%3d.%s" % (n, x))

        if re.match(r"^\$ULTW.*", footer, re.M | re.I):
            # # __________________________________________________________________________________
            # $ indicates a Ultimeter 2000
            # $ULTW 0000 0000 01FF 0004 27C7 0002 CCD3 0001 026E 003A 050F 0004 0000
            u"""
            Field #1,  0000 = Wind Speed Peak over last 5 min. ( reported as 0.1 kph increments)
            Field #2,  0000 = Wind Direction of Wind Speed Peak (0-255)
            Field #3,  01FF = Current Outdoor Temp (reported as 0.1 deg F increments) i.e. 01FF = 511 decimal * 0.1 = 51.1 deg F
            Field #4,  0004 = Rain Long Term Total (reported in 0.01 in. increments) 0.04 inches in this example
            Field #5,  27C7 = Current Barometer (reported in 0.1 mbar increments) 27C7 = 10183 decimal = 1018.3
            Field #6,  0002 = Barometer Delta Value(reported in 0.1 mbar increments)
            Field #7,  CCD3 = Barometer Corr. Factor(LSW)
            Field #8,  0001 = Barometer Corr. Factor(MSW)
            Field #9,  026E = Current Outdoor Humidity (reported in 0.1% increments) You know the drill now...
            Field #10, 003A = 10. Date (day of year since January 1) 58 decimal in this case... it was February 28th, 30 + 28 for Jan and Feb.
            Field #11, 050F = Time (minute of day) 1295 in this case after conversion to decimal.
            Field #12, 0004 = Today's Rain Total (reported as 0.01 inch increments)* 0.04 inches in this example
            Field #13, 0000 = 1 Minute Wind Speed Average (reported in 0.1kph increments)*
            """

            logger.debug(u"2 Ultimeter 2000")
            message_bytes = (5, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 0)
            fields = parseMessage(footer, message_bytes)

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

            logger.debug(u"2 Raw Weather Report")
            message_bytes = (1, 8, 1, 9, 1, 0)
            fields = parseMessage(footer, message_bytes)

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

            logger.info(u"_3a Positionless Weather Report")
            message_bytes = (1, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 1, 4, 0)
            # fields = parseMessages(footer, message_bytes)

            logger.info(u"_3b Positionless Weather Report")
            # MDHM
            message_bytes = (1, 4, 4, 4, 4, 4, 4, 4, 4, 4, 3, 6, 1, 3, 0)
            fields = parseMessage(footer, message_bytes)

        elif re.match(r"^=.*", footer, re.M | re.I):
            # __________________________________________________________________________________
            # Complete Weather Report Format - with Lat/Log position, no Timestamp
            # =2835.63NS08118.08W#PHG8250/DIGI_NED: OCCA Digi,www.w4mco.org,N2KIQ@arrl.net
            # =           Message
            # 2835.63N    Latitude
            # S           Symbol Table ID
            # 08118.08W   Longitude
            # #PHG8250/DIGI_NED: OCCA Digi,www.w4mco.org,N2KIQ@arrl.net

            logger.debug(u"4a Complete Weather Report")
            message_bytes = (1, 8, 1, 9, 0)
            fields = parseMessage(footer, message_bytes)

            logger.debug(u"4b Complete Weather Report")
            message_bytes = (1, 1, 4, 4, 1, 2, 1, 4, 4, 4, 4, 4, 4, 3, 6, 0)
            # fields = parseMessage(footer, message_bytes)

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

            if message[1][26] == u"_":
                logger.info(u"5b Complete Weather Format")
                message_bytes = (1, 7, 8, 1, 9, 1, 7, 4, 4, 4, 4, 4, 3, 6, 0)
                fields = parseMessage(footer, message_bytes)
            else:
                logger.info(u"5a Complete Weather Format")
                message_bytes = (1, 7, 8, 1, 9, 4, 4, 4, 4, 4, 4, 3, 6, 0)
                fields = parseMessage(footer, message_bytes)

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

            logger.debug(u"6 Complete Weather Report Format ")
            message_bytes = (1, 7, 8, 1, 9, 1, 7, 4, 4, 4, 4, 4, 3, 6, 1, 0)
            fields = parseMessage(footer, message_bytes)

        elif re.match(r";.*", footer, re.M | re.I):
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

            logger.debug(u"8 Object Report Format")

            message_bytes = (1, 9, 1, 7, 8, 1, 9, 1, 7, 0)
            fields = parseMessage(footer, message_bytes)

            message_bytes = (1, 9, 1, 7, 13, 43)
            #fields = parseMessage(footer, message_bytes)

        elif re.match(r">.*", footer, re.M | re.I):
            #
            # >- aprsfl.net/weather - New Port Richey WX
            logger.debug(u"9 Unknown")
            logger.debug(u"9\theader [%s]" % header)
            logger.debug(u"9\tfooter [%s]" % footer)

        elif re.match(r":.*", footer, re.M | re.I):
            # __________________________________________________________________________________
            # :
            # :

            logger.debug(u"8 Object Report Format")

            message_bytes = (1, 9, 1, 67, 1, 0)
            fields = parseMessage(footer, message_bytes)

        elif footer[0] == "`":
            # __________________________________________________________________________________
            # MicE Format
            # `
            m = u"M0XER-4>APRS64,TF3RPF,WIDE2*,qAR,TF3SUT-2:%s" % footer
            logger.debug(u"9 emic Format")
            result = aprslib.parse(m)

            for n, emix in enumerate(result):
                part = result[emix]
                if isinstance(part, (str, unicode)):
                    logger.info(u"   %s : %s" % (emix, part))
                elif isinstance(part, int):
                    logger.info(u"   %s : %3d" % (emix, part))
                elif isinstance(part, float):
                    logger.info(u"   %s : %3.3f" % (emix, part))
                else:
                    logger.info(u"   %s : tbd" % emix)

        else:
            # __________________________________________________________________________________

            logger.debug(u"No match - %s" % footer)


def grabOptions(av):
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


if __name__ == u"__main__":
    logFile = None
    opts = None
    program = u""

    program, ifile, ofile = grabOptions(sys.argv)

    if ifile == u"":
        logFile = u"messages%stest_messages_2016_0804_2015.txt" % os.sep

        try:
            logFl = get_GQRX_Output()

            for lf in logFl:
                with open(lf, "rb") as f:
                    messages = f.read()

                msgs = getMessages(messages)

                decodeMessages(msgs)

        except KeyboardInterrupt:
            logger.info(u"Bye ")
