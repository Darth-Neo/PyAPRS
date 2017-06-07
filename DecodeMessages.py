#!/usr/bin/env python
# -*- coding: utf-8 -*-
import aprslib
from GetPid import *
from ParseMessages import *
from rmq.rmq_send import *
from pymongo import *

from Logger import *
logger = setupLogging(__name__)
logger.setLevel(INFO)

client = MongoClient(u'mongodb://localhost:27017/')
database = u"local"
collection = u"Weather"
CLEAR_DB = False  # True

SLEEP_TIME = 10  # 5 minutes times 60 seconds

configFile = u"." + os.sep + u"rmq" + os.sep + u"rmq_settings.conf"
logger.info(u"%s" % configFile)
rbs = RabbitSend(configFile=configFile)
CLEAR_MESSAGES = False

weather_message = u""


def log_aprs_message(result):
        """
        Logs eMic messages that have special decoding needs
        :param result:
        :return:
        """

        for n, emix in enumerate(result):
            try:
                part = result[emix]
                if isinstance(part, (str, unicode)):
                    logger.info(u"       %s : %s" % (emix, part))
                elif isinstance(part, int):
                    logger.info(u"       %s : %3d" % (emix, part))
                elif isinstance(part, float):
                    logger.info(u"       %s : %3.3f" % (emix, part))
                else:
                    logger.info(u"       %s : tbd" % emix)
            except Exception, msg:
                logger.error(u"%s" % msg)


def get_gqrx_log_files(test=False):
    """
    Get the log file to decode
    :param test:
    :return:
    """
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
    """
    Get APRS Messages
    :param messages:
    :return:
    """
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


def update_display(message, gm=None):
    """
    :param message:
    :param gm:
    :return:
    """

    global rbs
    global weather_message

    if message is None:
        return

    fm = to = mt = None

    wl = list()
    # Preferred fields
    gm = [u"Temperature", u"Humidity", u"Barometer", u"Barometric Pressure", u"ReadingDateTime",
          # u"Time", u"Zulu Time",
          # u"symbol", u"symbol_table", u"Alternate Symbol Table",
          # u"longitude", u"latitude", u"Longitude", u"Latitude",
          # u"object_name",
          u"Rainfall Since Midnight", u"Rainfall In The Last Hour", u"Rainfall In The Last 24 Hour",
          # u"Course/Speed", u"altitude", u"course", u"speed",
          u"Wind Gust", u"Wind Speed PeaK", u"Wind Direction",
          # u"wx_raw_timestamp",
          # u"Message_Type",
          u"Comment"
          ]

    try:
        # Send To - From fields to Display
        to = message.pop(u"To", None)
        fm = message.pop(u"From", None)

        rbs.send_message(u"From: {}\n{} To: {}".format(fm, message[u"Message_Type"][0], to))

        # Begin queueing messages
        for k, v in sorted(message.items(), reverse=False):
            if k in gm:
                logger.debug(u"*** Match : {0} ***".format(v))
                if isinstance(v, float) and v != 0:
                    v = u"%4.2f" % v
                elif isinstance(v, int) and v != 0:
                    v = u"%4d" % v
                else:
                    continue

                rbs.send_message(u"%s\n%s" % (k.title(), v))

        # Finish by sending the Date and Time + Temp + Humidity + Barometric Pressure
        wmt = parse_weather_message(message)
        if wmt is None:
            dtt = datetime.now().strftime(u"%b %d  %I:%M %p") + os.linesep + weather_message
            rbs.send_message(dtt)
        else:
            dtt = datetime.now().strftime(u"%b %d  %I:%M %p") + os.linesep + wmt
            weather_message = wmt
            rbs.send_message(dtt)

    except Exception as e:
        logger.warn(u"{} {} {}".format(sys.exc_info()[-1].tb_lineno, type(e), e))


def queue_display(message, header=None, footer=None):
    """
    Queue up messages via RabbitMQ
    :param message:
    :param header:
    :param footer:
    :return:
    """
    global client
    global CLEAR_DB
    global database
    global collection

    if message is None:
        return

    db = client[database]
    c = db[collection]

    if CLEAR_DB is True:
        logger.debug(u"Reset MongoDB")
        c.remove()
        CLEAR_DB = False

    nf = {k.title(): v for k, v in message.items()}

    if not(u"Footer" in nf):
        nf[u"Footer"] = footer

    if not(u"Header" in nf):
        nf[u"Header"] = header

    if not(u"Message_Type" in nf):
        nf[u"Message_Type"] = footer[0]

    if not (u"ReadingDateTime" in nf):
        nf[u"ReadingDateTime"] = datetime.now().strftime(u"%b %d  %I:%M %p")

    log_aprs_message(nf)

    logger.debug(u"_____________________________________________________________________________")

    c.insert_one(nf)

    update_display(nf)


# Decode all messages
def decode_aprs_messages(msgs):
    """
    Decode APRS Messages
    :param msgs:
    :return:
    """

    for n, message in enumerate(msgs):

        try:
            header = message[0].lstrip()
            footer = message[1].lstrip()

            header_fields, aprs_addresses = parse_aprs_header(header, footer, n=n)

            logger.debug(u"%3d [%s]" % (n, header[10:]))
            logger.debug(u"    [%s]" % footer)

            # 1 $ULTW
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
                #        1    2    3    4      5     6    7      8    9     10   11   12   13
                # $ULTW 0018 0060 02D8 8214  27C4   0003 8702   0001 03E8  0099 0050 0000 0001
                # $ULTW 0000 0000 02D3 670F  27BC   FFFD 8765   0001 03E8  0099 0046 0001 0000
                # $ULTW 00B0 0042 02D3 25ED  27C2   0010 8935   0001 03E8  0098 050A 0037 006A
                # $ULTW 0064 00AB 030C 1821  2784   0001 85E5   0001 0323  009B 058C 0000 0026
                #        1.7 66   72.3 97.09 1017.8 1.6  35125  1    100.0 152  1290 0.55 10.6
                # rem = u"^$ULTW[0-9a-zA-Z]{52}"
                try:
                    logger.debug(u"1 Ultimeter 2000")
                    message_bytes = (5, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 0)
                    fields = parse_aprs_footer(footer, message_bytes)
                    fields[u"Message_Type"] = u"$ULTW"
                    fields.update(header_fields)
                    if fields[u"Wind Direction"] == 0:
                        fields[u"Wind Direction"] = u"N"
                    queue_display(fields, header=header, footer=footer)

                except Exception as e:
                    logger.warn(u"{} {} {}".format(sys.exc_info()[-1].tb_lineno, type(e), e))

            # 2 aprslib _
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
                #           1           2            3           4          5         6
                # 123456789 0123 4567 8901 2345 6789 0123 4567 890 123456 78901234567890123456789
                # _05311550 c359 s000 g000 t086 r000 p086 P000 h64 b10160 tU2k
                # _05312040 c359 s000 g000 t075 r000 p086 P035 h99 b10182 tU2k
                # _06051349 c359 s000 g000 t081 r000 p037 P023 h89 b10084 tU2k
                # rem = u"^_\d{8}c\d{3}s\d{3}g\d{3}t\d{3}r\d{3}p\d{3}P\d{3}h\d{2}b\d{5}.*"
                # 1 8 c 3 s 3 g 3 t 3 r 3 p 3 P 3 h 2 b 5
                try:  # This seems to fail alot
                    rem = u"^_\d{8}c\d{3}s\d{3}g\d{3}t\d{3}r\d{3}p\d{3}P\d{3}h\d{2}b\d{5}.*"
                    if re.match(rem, footer, re.M):
                        logger.info(u"2a Raw Weather Report")
                        fields = aprslib.parse(aprs_addresses)
                        fields[u"Message_Type"] = u"_a"
                        fields.update(header_fields)
                        nf = {k.title(): v for k, v in fields[u"weather"].items()}
                        del fields[u"weather"]
                        nfa = {k.title(): v for k, v in nf.items()}
                        queue_display(nfa, header=header, footer=footer)

                except Exception, msg:
                    try:
                        # MDHM
                        logger.info(u"2b Positionless Weather Report")
                        message_bytes = (1, 4, 4, 4, 4, 4, 4, 4, 4, 4, 3, 6, 1, 3, 0)
                        fields = parse_aprs_footer(footer, message_bytes)
                        fields[u"Message_Type"] = u"_b"
                        fields.update(header_fields)
                        queue_display(fields, header=header, footer=footer)

                    except Exception, msg:
                        logger.info(u"2c Positionless Weather Report")
                        message_bytes = (1, 4, 4, 4, 4, 4, 4, 4, 4, 4, 3, 5, 1, 4, 0)
                        fields = parse_aprs_footer(footer, message_bytes)
                        fields[u"Message_Type"] = u"_c"
                        fields.update(header_fields)
                        queue_display(fields, header=header, footer=footer)

            # 3 aprslib !
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
                # !2818.17N/08209.50W#Dade City
                # rem = u"^!\d{4}.\d{2}(N|S).+\d{4}.\d{2}(E|W).+"
                try:
                    logger.info(u"3a Raw Weather Report")
                    fields = aprslib.parse(aprs_addresses)
                    fields[u"Message_Type"] = u"!a"
                    fields.update(header_fields)
                    queue_display(fields, header=header, footer=footer)

                except Exception, msg:
                    logger.debug(u"2 %s" % msg)
                    logger.info(u"3b Raw Weather Report")
                    message_bytes = (1, 8, 1, 9, 1, 0)
                    fields = parse_aprs_footer(footer, message_bytes)
                    fields[u"Message_Type"] = u"!b"
                    fields.update(header_fields)
                    queue_display(fields, header=header, footer=footer)

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
                #
                #              1           2            3           4          5         6
                # 0 12345678 9 012345678 9 0123456789 0123 4567 890 123456 78901234567890123456789
                # = 2835.63N S 08118.08W # PHG8250/DIGI_NED: OCCA Digi,www.w4mco.org,N2KIQ@arrl.net
                # = 2751.41N / 08248.28W _ PHG2160/NB9X Weather Station -FLPINSEMINOLE-285-<630>
                # = 2816.97N S 08242.70W # PHG74326/W3 Digi, Port Richey, FL aprsfl.net
                # = 2816.98N / 08242.70W I West Pasco I-Gate 200ft AGL aprsfl.net'
                rem = u"^=\d{4}.\d{2}(N|S){1}.+\d{4}.\d{2}(E|W){1}.+"
                try:
                    if re.match(rem, footer, re.M):
                        logger.info(u"4a Complete Weather Report")
                        message_bytes = (1, 8, 1, 9, 1, 0)
                        flds = parse_aprs_footer(footer, message_bytes, grab_fields=False)

                        fields = dict()
                        fields.update(header_fields)
                        fields[u"Message_Type"] = flds[0]
                        fields[u"Longitude"] = flds[1]
                        fields[u"Symbol_Table"] = flds[2]
                        fields[u"Latitude"] = flds[3]
                        fields[u"Symbol"] = flds[4]
                        fields[u"Comments"] = flds[4]
                        queue_display(fields, header=header, footer=footer)
                    else:
                        pass
                except Exception, msg:
                    logger.warn(u"4 %s" % msg)
                    logger.info(u"4b Complete Weather Report")
                    message_bytes = (1, 1, 4, 4, 1, 2, 1, 4, 4, 4, 4, 4, 4, 3, 6, 0)
                    fields = parse_aprs_footer(footer, message_bytes)
                    fields.update(header_fields)
                    fields[u"Message_Type"] = u"=b"
                    queue_display(fields, header=header, footer=footer)

                    try:
                        logger.info(u"4 Complete Weather Report")
                        fields = aprslib.parse(aprs_addresses)
                        fields.update(header_fields)
                        fields[u"Message_Type"] = u"=c"
                        queue_display(fields, header=header, footer=footer)

                    except Exception, msg:
                        logger.warn(u"4 %s" % msg)

            # 5 aprslib @
            elif re.match(r"^@.*", footer, re.M | re.I):
                fields = dict()
                fields[u"Message_Type"] = u"@"
                fields[u"header"] = header
                fields[u"footer"] = footer

                #              1            2             3            4         5         6
                # 0 123456 7 8901234 5 6 78901234 5 6 7 89012 3456789012345678901234567890123456789
                # @ 022230 z 2813.12 N / 08214.30 W _ 138/000 g002t079r000p000P000Zephyrhills WX {UIV32N}
                # @ 170008 z 2831.07 N / 08142.92 W _ 000/000 g002t094r000p000P000h49b10150.DsVP
                # @ 311706 z 2815.27 N S 08139.28 W _ PHG74606/W3,FLn Davenport, Florida
                # @ 311657 z 2752.80 N S 08148.94 W _ PHG75506/W3,FLn-N Bartow, Florida
                # @ 095148 h 2835.66 N / 08118.09 W o Orange County ARES
                #
                # ^@\d{6}(h|z){1}\d{4}.\d{2}(N|S){1}.\d{4}\.\d{2}(E|W){1}.+
                if footer[15] == u"N" and footer[25] == u"W":

                    fields[u"Time"] = footer[1:6]
                    fields[u"Latitude"] = footer[8:16]
                    fields[u"Longitude"] = footer[17:26]
                    fields[u"Symbol_Table"] = footer[16]
                    fields[u"Symbol"] = footer[26]

                    # Wind Gust
                    if footer[34] == u"g":
                        fields[u"Wind Gust"] = int(footer[35:38])

                    # Temperature
                    if footer[38] == u"t":
                        if footer[39] == u"0":
                            fields[u"Temperature"] = footer[40:42]
                        else:
                            fields[u"Temperature"] = footer[39:42]

                    # Rain in the last hour
                    if footer[42] == u"r":
                        fields[u"Rainfall In The Last hour"] = footer[43:44] + u"." + footer[44:45]

                    # Rain in the last 24 hours
                    if footer[46] == u"p":
                        fields[u"Rainfall In The Last 24 hour"] = footer[47:48] + u"." + footer[48:50]

                    # Rain since midnight
                    if footer[50] == u"P":
                        fields[u"Rainfall Since Midnight"] = footer[51:52] + u"." + footer[52:54]

                    # Humidity
                    if footer[54] == u"h":
                        fields[u"Humidity"] = int(footer[55:57])

                    # Barometer
                    if footer[57] == u"b":
                        fields[u"Barometer"] = footer[58:62] + u"." + footer[62]

                    if fields is not None:
                        fields[u"Message_Type"] = u"@a"
                        fields.update(header_fields)
                        queue_display(fields, header=header, footer=footer)
                else:

                    # __________________________________________________________________________________
                    # Complete Weather Format
                    # @ 220605 z 2831.07N / 08142.92W _000/000 g002 t100 r000 p000 P000 h46 b10144.DsVP
                    # @ 220605 z 2831.07N / 08142.92W _000/000 g002 t100 r000 p000 P000 h46 b10144 .DsVP.
                    # @ Message
                    # 22 06 05z Zulu Time
                    # 2831.07N  Latitude
                    # 08142.92W Longitude
                    # g002      Wind Gust in the last five minutes
                    # t100      Temperature
                    # r000      Rainfall in the last hour
                    # p000      Rainfall in the last 24 hours
                    # P000      Rainfall since midnight
                    # h46       Humidity
                    # b10144    Barometric Pressure
                    #
                    # ^@\d{6}[h|z]{1}\d{4}\.\d{2}[N|S]{1}.\d{4}\.\d{2}[E|W]{1}.\d{3}.\d{3}g\d{3}t\d{3}r\d{3}p\d{3}P\d{3}h\d{3}b\d{5}.+
                    try:
                        logger.info(u"5 Complete Weather Format")
                        fields = aprslib.parse(aprs_addresses)
                        fields[u"Message_Type"] = u"@b"
                        fields.update(header_fields)
                        queue_display(fields, header=header, footer=footer)

                    except Exception, msg:
                        try:
                            logger.info(u"5b Complete Weather Format")
                            message_bytes = (1, 7, 8, 1, 9, 1, 7, 4, 4, 4, 4, 4, 3, 6, 0)
                            fields = parse_aprs_footer(footer, message_bytes)
                            fields[u"Message_Type"] = u"@c"
                            fields.update(header_fields)
                            queue_display(fields, header=header, footer=footer)

                        except Exception, msg:
                            logger.info(u"5c Complete Weather Format")
                            message_bytes = (1, 7, 8, 1, 9, 4, 4, 4, 4, 4, 4, 3, 6, 0)
                            fields = parse_aprs_footer(footer, message_bytes)
                            fields[u"Message_Type"] = u"@d"
                            fields.update(header_fields)
                            queue_display(fields, header=header, footer=footer)

            # 6 aprslib /
            elif re.match(r"^/.*", footer, re.M | re.I):
                # __________________________________________________________________________________
                # Complete Weather Report Format — with Compressed Lat/Long position, with Timestamp
                # / 311704z 2757.15N / 08147.20W _ 103/008 g012 t094 r000 p001 P000 h41 b10183
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
                #
                #               1           2            3           4             5            6
                # 0 123456  7 89012345 6 789012345 6 789 0 123 4567 8901 2345 6789 012 345678 9 012345
                # / 011851  z 2803.50N / 08146.10W _ 051/000 g006 t096 r000 P000 h45 b10161 w VL1252
                # 1      6  1       8 1         9 1       7    4    4    4    4   3      6 1      6
                # rem = u"^/\d{6}z[\d.n]{8}/[\d.W]{9}_[\d/]{7}g\d{3}t[\d]{3}r\d{3}P\d{3}h\d{2}b\d{4}.*"
                try:
                    rem = u"/\d{6}z[\d.n]{8}/[\d.W]{9}_[\d/]{7}g\d{3}t[\d]{3}r\d{3}P\d{3}h\d{2}b\d{4}.*"
                    if re.match(rem, footer, re.I):
                        logger.info(u"6 Complete Weather Report Format ")
                        fields = aprslib.parse(aprs_addresses)
                        fields[u"Message_Type"] = u"/a"
                        fields[u"Symbol"] = fields[u"Footer"][26]
                        fields.update(header_fields)
                        queue_display(fields, header=header, footer=footer)

                except Exception, msg:
                    logger.debug(u"5 %s" % msg)
                    try:
                        logger.info(u"6 Complete Weather Report Format ")
                        message_bytes = (1, 7, 8, 1, 9, 1, 7, 4, 4, 4, 4, 3, 6, 1, 0)
                        fields = parse_aprs_footer(footer, message_bytes)
                        fields[u"Message_Type"] = u"/b"
                        fields.update(header_fields)
                        queue_display(fields, header=header, footer=footer)

                    except Exception, msg:
                        logger.debug(u"6 Trying alternate parsing : %s" % msg)

            # 7 aprslib ;
            elif re.match(r"^;.*", footer, re.M | re.I):
                # __________________________________________________________________________________
                # ;145.650  * 051916 z 2749.31N / 08244.16W r/A=000025AA/Cert-Node 273835
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
                # ";443.050- *111111z2832.38N\\08122.79Wy T103 R40m Skywarn w4mco.org "
                # ";443.075+ *061653z2833.11N/08123.12WrCFRA",
                # ";443.050- *111111z2832.38N\\08122.79Wy T103 R40m Skywarn w4mco.org "
                # rem = u"^;\d{3}.\d{3}.{3}\d{6}(z|h)\d{4}.\d{2}(N|S){1}.+\d{4}\.\d{2}(E|W){1}.+
                try:
                    logger.info(u"7a Object Report Format")
                    fields = aprslib.parse(aprs_addresses)
                    fields[u"Message_Type"] = u";a"
                    fields.update(header_fields)
                    queue_display(fields, header=header, footer=footer)

                except Exception, msg:
                    logger.info(u"7b Object Report Format")

                    try:
                        message_bytes = (1, 9, 1, 7, 8, 1, 9, 1, 7, 0)
                        fields = parse_aprs_footer(footer, message_bytes)
                        fields[u"Message_Type"] = u";b"
                        fields.update(header_fields)
                        queue_display(fields, header=header, footer=footer)

                    except Exception, msg:  # else:
                        logger.info(u"7c %s" % msg)
                        message_bytes = (1, 9, 1, 7, 13, 43)
                        fields = parse_aprs_footer(footer, message_bytes)

                        if not (fields is None):
                            fields[u"Message_Type"] = u";c"
                            fields.update(header_fields)
                            queue_display(fields, header=header, footer=footer)

            # 8 aprslib >
            elif re.match(r"^>.*", footer, re.M | re.I):
                #
                # >- aprsfl.net/weather - New Port Richey WX
                # >DIGI_NED: W4MCO-10 digipeater in Winter Park, FL
                try:
                    logger.info(u"8 Unknown")
                    fields = aprslib.parse(aprs_addresses)
                    fields[u"Message_Type"] = u">"
                    queue_display(fields, header=header, footer=footer)

                except Exception, msg:
                    logger.error(u"8 %s" % msg)

            # 9 aprslib :
            elif re.match(r"^:.*", footer, re.M | re.I):
                # __________________________________________________________________________________
                # :BLN3     :OCARES Net tonite at 1900 hrs. Please send check-ins to KG4CWV.{005"
                # rem = u"^:.+"
                rem = u"^:"
                logger.info(u"9 Object Report Format")

                try:
                    fields = aprslib.parse(aprs_addresses)
                    fields[u"Message_Type"] = u":a"
                    queue_display(fields, header=header, footer=footer)
                except Exception, msg:
                    logger.warn(u"9 %s" % msg)
                    message_bytes = (1, 9, 1, 67, 1, 0)
                    fields = parse_aprs_footer(footer, message_bytes)
                    fields[u"Message_Type"] = u":b"
                    fields.update(header_fields)
                    queue_display(fields, header=header, footer=footer)

            # 10 aprslib `
            elif re.match(r"^`.*", footer, re.M | re.I):
                # __________________________________________________________________________________
                # MicE Format
                # `
                logger.info(u"10 eMic Format")
                fields = aprslib.parse(aprs_addresses)
                fields[u"Message_Type"] = u"MicE"
                fields.update(header_fields)
                queue_display(fields, header=header, footer=footer)

            else:
                # _____________________________________
                logger.debug(u"No match - %s" % footer)

        except Exception as e:
            logger.warn(u"decode_aprs_messages {} {} {}".format(sys.exc_info()[-1].tb_lineno, type(e), e))
            continue


def loop_decode_messages(test=False):
    """
    Loop messages and decode as needed
    """
    cw = os.getcwd()
    ofn = cw + os.sep + u"DecodeMessageLine.sl"

    while True:
        try:
            logFl = get_gqrx_log_files(test=test)

            eofl = loadObject(ofn)
            for n, lf in enumerate(logFl):
                if lf not in eofl.keys():
                    with open(lf, "rb") as f:
                        messages = f.read()
                        eofl[lf] = (f.tell(), lf)
                        logger.debug(u"%d : %s" % (f.tell(), lf))

                else:
                    eofm = eofl[lf][0]
                    logger.debug(u"eofm = %d" % eofm)
                    with open(lf, "rb") as cf:
                        cf.seek(eofm)
                        messages = cf.read()
                        if len(messages) > 0:
                            eofl[lf] = (cf.tell(), lf)
                            logger.debug(u"%d : %s" % (cf.tell(), lf))

                saveObject(eofl, ofn)
                msgs = get_aprs_messages(messages)
                decode_aprs_messages(msgs)

            time.sleep(SLEEP_TIME)

        except Exception, msg:
            logger.debug(u"%s" % msg)
            logFl = get_gqrx_log_files(test=test)


if __name__ == u"__main__":

    if False:
        fpn = u"mongpd"
        process_found, pid, sp = getPID(fpn)

        if process_found is False:
            logger.error(u"Need to start %s first!" % fpn)
            logger.info(u"Did you start GQRX from gogqrx.sh?")
            sys.exit(1)

    try:
        # program, ifile, ofile = get_CommandLine_Options(sys.argv)

        loop_decode_messages(test=False)

    except KeyboardInterrupt:
        logger.info(u"Bye")
