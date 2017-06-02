#!/usr/bin/env python
# -*- coding: utf-8 -*-
import getopt
import hashlib
import aprslib
import geo_lib
from GetPid import *
from ListAngle import *
from ParseMessages import *
# from aprs_table_and_symbols import *
from rmq.rmq_send import *

from Logger import *
logger = setupLogging(__name__)
logger.setLevel(INFO)


MongoPersist = False
client = MongoClient(u'mongodb://localhost:27017/')
database = u"local"
collection = u"Weather"
CLEAR_DB = False  # True

SLEEP_TIME = 10  # 5 minutes times 60 seconds

configFile = u"." + os.sep + u"rmq" + os.sep + u"rmq_settings.conf"
logger.info(u"%s" % configFile)
rbs = RabbitSend(configFile=configFile)
CLEAR_MESSAGES = False
message_counter = dict()

if False:
    def run_cmd(cmd):
        """
        Executee a command
        :param cmd:
        :return:
        """
        p = Popen(cmd, shell=True, stdout=PIPE)
        output = p.communicate()[0]
        return output


    def get_CommandLine_Options(av):
        """
        Get Options from the command line
        :param av:
        :return:
        """
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
                logger.debug(u"%s -i <inputfile> -o <outputfile>" % program)
                sys.exit()

            elif opt in (u"-i", u"--ifile"):
                inputfile = arg

            elif opt in (u"-o", u"--ofile"):
                outputfile = arg

        logger.debug(u"Input file is %s" % inputfile)
        logger.debug(u"'Output file is %s" % outputfile)

        return program, inputfile, outputfile


    def __decode_messages(test=True):
        """
        Decode Messages
        :param test:
        :return:
        """

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
                logger.info(u"Message Type Counts :  %4d " % mc)

                output = u"Top Ten : "
                for key, value in mts[:10]:
                    output += u"%s[%s] " % (key, value)

                logger.info(u"%s" % output)

        except KeyboardInterrupt:
            logger.info(u"Bye ")


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


def prepare_display(message, gm=None, ALL_FIELDS=False, DISPLAY_MESSAGE_COUNTS=False):
    """
    :param message:
    :param gm:
    :param ALL_FIELDS:
    :param DISPLAY_MESSAGE_COUNTS:
    :return:
    """

    global rbs

    fm = to = mt = None

    wl = list()

    try:
        if message is None:
            return

        # Send To - From fields to Display
        if u"to" in message:
            to = message.pop(u"to", None)
            fm = message.pop(u"from", None)

        elif u"To" in message:
            to = message.pop(u"To", None)
            fm = message.pop(u"From", None)

        if u"Message_Type" in message:
            mt = message.pop(u"Message_Type", None)
            rbs.send_message(u"From: {}\n{} To: {}".format(fm, mt[0], to))
        else:
            rbs.send_message(u"From: {}\n  To: {}".format(fm, to))

        try:
            if u"longitude" in message:
                logger.debug(u"longitude : %s" % message[u"longitude"])
                logger.debug(u"latitude : %s" % message[u"latitude"])

                lat = abs(message.pop(u"latitude", None))
                lon = abs(message.pop(u"longitude", None))
                gl = geo_lib.calculateFromHome(lat, lon, display=True)
                if gl is not None:
                    logger.debug(u"Miles   : %3.2f" % (gl[0][0]))
                    logger.debug(u"Compass : %3.2f %s" % (gl[2][1], gl[1][1]))
                    rbs.send_message(u"Miles : %3.2f\nCompass %3.2f %s" % (gl[0][0], gl[2][1], gl[1][1]))

            elif u"Longitude" in message:
                logger.debug(u"Longitude : %s" % message[u"Longitude"])
                logger.debug(u"Latitude : %s" % message[u"Latitude"])

                if re.match(r"[0-9]{4}.[0-9]{2}[NS]", message[u"Latitude"], re.M | re.I) and \
                        re.match(r"[0-9]{5}.[0-9]{2}[WE]", message[u"Longitude"], re.M | re.I):

                    lat = message.pop(u"Latitude", None)
                    lon = message.pop(u"Longitude", None)
                    gl = geo_lib.calculateFromHome(lat, lon, display=True)
                    if gl is not None:
                        logger.debug(u"Miles   : %3.2f" % (gl[0][0]))
                        logger.debug(u"Compass : %3.2f %s" % (gl[2][1], gl[1][1]))
                        rbs.send_message(u"Miles : %3.2f\nCompass %3.2f %s" % (gl[0][0], gl[2][1], gl[1][1]))
        except Exception, msg:
            logger.debug(u"%s" % msg)

        # Preferred fields
        if gm is None:
            gm = [u"Temperature", u"Humidity", u"Barometer", u"Barometric Pressure",
                  # u"Time", u"ReadingDateTime", u"Zulu Time",
                  # u"symbol", u"symbol_table", u"Alternate Symbol Table",
                  # u"longitude", u"latitude", u"Longitude", u"Latitude",
                  # u"object_name",
                  u"Rainfall since midnight", u"Rainfall in the last hour", u"Rainfall in the last 24 hour",
                  # u"Course/Speed", u"altitude", u"course", u"speed",
                  u"Wind Gust", u"Wind Speed PeaK", u"Wind Direction",
                  # u"wx_raw_timestamp",
                  # u"Message_Type",
                  u"comment"
                  ]

        # Begin displaying messages
        for k, v in sorted(message.items(), reverse=False):
            if isinstance(v, dict):
                for k1, v1 in v.items():
                    logger.debug(u"{0} : {1}".format(k1, v1))
            else:
                logger.debug(u"{0} : {1}".format(k, v))

            if ALL_FIELDS or k in gm:
                if v is not None:
                    logger.debug(u"*** Match : {0} ***".format(v))
                    if isinstance(v, float) and v != 0:
                        v = u"%4.2f" % v
                    elif isinstance(v, int) and v != 0:
                        v = u"%4d" % v
                    else:
                        continue

                    rbs.send_message(u"%s\n%s" % (k.title(), v))

        # Send all weather measurements to display
        if u"weather" in message:
            nm = message[u"weather"]
            nm.pop(u"via", None)
            nm.pop(u"messagecapable", None)
            nm.pop(u"posambiguity", None)
            nm.pop(u"format", None)

            for k, v in sorted(nm.items(), reverse=False):
                if v is not None:
                    if isinstance(v, float) and v != 0.0:
                        v = u"%4.2f" % v
                    elif isinstance(v, int) and v != 0:
                        v = u"%4d" % v
                    else:
                        continue

                    logger.debug(u"%s -- %s" % (k.title(), v))
                    rbs.send_message(u"%s\n%s" % (k.title(), v))

        # Decode the symbol based on symbol table
        if u"symbol" in message and u"symbol_table" in message:
            symbol_table = message[u'symbol_table']
            symbol = message[u'symbol']
            vl = findSymbolName(symbol_table, symbol)
            output = u"[%s%s] : %s" % (symbol_table, symbol, vl)
            logger.debug(output)
            rbs.send_message(output)

        # Display message counts
        minute = datetime.now().minute
        if DISPLAY_MESSAGE_COUNTS is True and minute in (0, 10, 20, 30, 40, 50):
            for k, v in message_counter.items():
                mt = message_types[k]
                output = u"{}\n{}".format(mt, v)
                rbs.send_message(output)

        wmsg = parse_message(message)
        if wmsg is None:
            # Finish by sending the Date and Time
            dtt = datetime.now().strftime(u"%b %d %Y\n%I:%M %p")
            rbs.send_message(dtt)
        else:
            dtt = datetime.now().strftime(u"%b %d  %I:%M %p") + os.linesep + wmsg
            rbs.send_message(dtt)

    except Exception, msg:
        logger.warn(u"%s" % msg)


def queue_display(message, header=None, footer=None, hash=False):
    """
    Queue up messages via RabbitMQ
    :param message:
    :param header:
    :param footer:
    :param hash:
    :return:
    """
    global client
    global CLEAR_DB
    global database
    global collection

    db = client[database]
    c = db[collection]

    logger.debug(u"_____________________________________________________________________________")

    if CLEAR_DB is True:
        logger.debug(u"Reset MongoDB")
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

    prepare_display(message)


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

            # Message Counter
            if footer[0] in message_counter:
                message_counter[footer[0]] += 1
            else:
                message_counter[footer[0]] = 1

            if re.match(r"^ *[0-9]+:[0-9]+:[0-9]+.*", header, re.M | re.I):
                logger.info(u"1 H.%3d PF    : %s " % (n, header))

                if logger.getEffectiveLevel() == DEBUG:
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
                    logger.debug(u"1 Ultimeter 2000")
                    message_bytes = (5, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 0)
                    fields = parse_aprs_footer(footer, message_bytes)
                    if fields is not None:
                        fields[u"Message_Type"] = u"$ULTW"
                        fields.update(header_fields)
                        log_aprs_message(fields)
                        queue_display(fields, header=header, footer=footer)

                except Exception, msg:
                    logger.warn(u"1 %s" % msg)

            # 2 _
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
                #
                #           1           2            3           4          5         6
                # 123456789 0123 4567 8901 2345 6789 0123 4567 890 123456 78901234567890123456789
                # _05311550 c359 s000 g000 t086 r000 p086 P000 h64 b10160 tU2k
                # _05312040 c359 s000 g000 t075 r000 p086 P035 h99 b10182 tU2k
                # _{1}\d{8}c\d{3}s\d{3}g\d{3}t\d{3}r\d{3}p\d{3}P\d{3}h\d{2}b\d{5}.*
                # 1 8 c 3 s 3 g 3 t 3 r 3 p 3 P 3 h 2 b 5
                try:
                    logger.info(u"2a Raw Weather Report")
                    fields = aprslib.parse(aprs_addresses)
                    if fields is not None:
                        fields[u"Message_Type"] = u"_"
                        fields.update(header_fields)
                        nf = {k.title(): v for k, v in fields[u"weather"].items()}
                        del fields[u"weather"]
                        nfa = {k.title(): v for k, v in nf.items()}
                        log_aprs_message(nfa)
                        queue_display(nfa, header=header, footer=footer)

                except Exception, msg:
                    try:
                        # MDHM
                        logger.info(u"2b Positionless Weather Report")
                        message_bytes = (1, 4, 4, 4, 4, 4, 4, 4, 4, 4, 3, 6, 1, 3, 0)
                        fields = parse_aprs_footer(footer, message_bytes)
                        if fields is not None:
                            fields[u"Message_Type"] = u"_"
                            fields.update(header_fields)
                            nf = {k.title(): v for k, v in fields.items()}
                            log_aprs_message(nf)
                            queue_display(nf, header=header, footer=footer)

                    except Exception, msg:
                        logger.info(u"2c Positionless Weather Report")
                        message_bytes = (1, 4, 4, 4, 4, 4, 4, 4, 4, 4, 3, 5, 1, 4, 0)
                        fields = parse_aprs_footer(footer, message_bytes)
                        if fields is not None:
                            fields[u"Message_Type"] = u"_"
                            fields.update(header_fields)
                            nf = {k.title(): v for k, v in fields.items()}
                            log_aprs_message(nf)
                            queue_display(nf, header=header, footer=footer)

            # 3 - aprslib !
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
                    logger.info(u"3a Raw Weather Report")
                    fields = aprslib.parse(aprs_addresses)
                    if fields is not None:
                        fields[u"Message_Type"] = u"!"
                        fields.update(header_fields)
                        log_aprs_message(fields)
                        queue_display(fields, header=header, footer=footer)

                except Exception, msg:
                    logger.debug(u"2 %s" % msg)
                    logger.info(u"3b Raw Weather Report")
                    message_bytes = (1, 8, 1, 9, 1, 0)
                    fields = parse_aprs_footer(footer, message_bytes)
                    if fields is not None:
                        fields[u"Message_Type"] = u"!"
                        fields.update(header_fields)
                        log_aprs_message(fields)
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
                # =2835.63NS08118.08W#PHG8250/DIGI_NED: OCCA Digi,www.w4mco.org,N2KIQ@arrl.net
                # =2751.41N/08248.28W_PHG2160/NB9X Weather Station -FLPINSEMINOLE-285-<630>

                try:
                    logger.info(u"4 Complete Weather Report")
                    fields = aprslib.parse(aprs_addresses)
                    if fields is not None:
                        fields.update(header_fields)
                        fields[u"Message_Type"] = u"="

                        log_aprs_message(fields)
                        queue_display(fields, header=header, footer=footer)

                except Exception, msg:
                    logger.warn(u"4 %s" % msg)
                    try:
                        logger.info(u"4a Complete Weather Report")
                        message_bytes = (1, 8, 1, 9, 1, 0)
                        fields = parse_aprs_footer(footer, message_bytes)
                        if fields is not None:
                            fields.update(header_fields)
                            log_aprs_message(fields)
                            fields[u"Message_Type"] = u"="
                            queue_display(fields, header=header, footer=footer)

                    except Exception, msg:
                        logger.warn(u"4 %s" % msg)
                        logger.info(u"4b Complete Weather Report")
                        message_bytes = (1, 1, 4, 4, 1, 2, 1, 4, 4, 4, 4, 4, 4, 3, 6, 0)
                        fields = parse_aprs_footer(footer, message_bytes)
                        if fields is not None:
                            fields.update(header_fields)
                            fields[u"Message_Type"] = u"="
                            log_aprs_message(fields)
                            queue_display(fields, header=header, footer=footer)

            # 5 aprslib @
            elif re.match(r"^@.*", footer, re.M | re.I):
                fields = dict()
                fields[u"Message_Type"] = u"@"

                #          1           2          3         4         5         6
                # 1234567890123456 7 890123456 7890123456789012345678901234567890123456789
                # @170008z2831.07N / 08142.92W _000/000g002t094r000p000P000h49b10150.DsVP
                # @311706z2815.27N S 08139.28W _PHG74606/W3,FLn Davenport, Florida
                # @311657z2752.80N S 08148.94W _PHG75506/W3,FLn-N Bartow, Florida
                # @095148h2835.66N / 08118.09W oOrange County ARES
                if footer[15] == u"N" and footer[25] == u"W":

                    fields[u"Time"] = footer[1:6]
                    fields[u"Latitude"] = footer[8:16]
                    fields[u"Longitude"] = footer[17:26]

                    # Wind Gust
                    if footer[34] == u"g":
                        fields[u"Wind Gust"] = footer[35:38]

                    # Temperature
                    if footer[38] == u"t":
                        if footer[39] == u"0":
                            fields[u"Temperature"] = footer[40:42]
                        else:
                            fields[u"Temperature"] = footer[39:42]

                    # Rain in the last hour
                    if footer[42] == u"r":
                        fields[u"Rainfall in the last hour"] = footer[43:44] + u"." + footer[44:45]

                    # Rain in the last 24 hours
                    if footer[46] == u"p":
                        fields[u"Rainfall in the last 24 hour"] = footer[47:48] + u"." + footer[48:50]

                    # Rain since midnight
                    if footer[50] == u"P":
                        fields[u"Rainfall since midnight"] = footer[51:52] + u"." + footer[52:54]

                    # Humidity
                    if footer[54] == u"h":
                        fields[u"Humidity"] = footer[55:57]

                    # Barometer
                    if footer[57] == u"b":
                        fields[u"Barometer"] = footer[58:62] + u"." + footer[62]

                    if fields is not None:
                        fields[u"Message_Type"] = u"@"
                        fields.update(header_fields)
                        log_aprs_message(fields)
                        nf = {k.title(): v for k, v in fields.items()}
                        queue_display(nf, header=header, footer=footer)
                else:

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
                        if fields is not None:
                            fields[u"Message_Type"] = u"@"
                            fields.update(header_fields)
                            log_aprs_message(fields)
                            nf = {k.title(): v for k, v in fields.items()}
                            queue_display(nf, header=header, footer=footer)

                    except Exception, msg:
                        try:
                            logger.info(u"5b Complete Weather Format")
                            message_bytes = (1, 7, 8, 1, 9, 1, 7, 4, 4, 4, 4, 4, 3, 6, 0)
                            fields = parse_aprs_footer(footer, message_bytes)
                            if fields is not None:
                                fields[u"Message_Type"] = u"@"
                                fields.update(header_fields)
                                log_aprs_message(fields)
                                nf = {k.title(): v for k, v in fields.items()}
                                queue_display(nf, header=header, footer=footer)

                        except Exception, msg:
                            logger.info(u"5c Complete Weather Format")
                            message_bytes = (1, 7, 8, 1, 9, 4, 4, 4, 4, 4, 4, 3, 6, 0)
                            fields = parse_aprs_footer(footer, message_bytes)
                            if fields is not None:
                                fields[u"Message_Type"] = u"@"
                                fields.update(header_fields)
                                log_aprs_message(fields)
                                nf = {k.title(): v for k, v in fields.items()}
                                queue_display(nf, header=header, footer=footer)

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
                # rem = "/\d{6}z[\d.n]{8}/[\d.W]{9}_[\d/]{7}g\d{3}t[\d]{3}r\d{3}P\d{3}h\d{2}b\d{4}.*"
                try:
                    rem = u"/\d{6}z[\d.n]{8}/[\d.W]{9}_[\d/]{7}g\d{3}t[\d]{3}r\d{3}P\d{3}h\d{2}b\d{4}.*"
                    if re.match(rem, footer, re.I):
                        logger.info(u"6 Complete Weather Report Format ")
                        fields = aprslib.parse(aprs_addresses)
                        if fields is not None:
                            fields[u"Message_Type"] = u"/"
                            fields.update(header_fields)
                            log_aprs_message(fields)
                            queue_display(fields, header=header, footer=footer)

                except Exception, msg:
                    logger.debug(u"5 %s" % msg)
                    try:
                        logger.info(u"6 Complete Weather Report Format ")
                        message_bytes = (1, 7, 8, 1, 9, 1, 7, 4, 4, 4, 4, 3, 6, 1, 0)
                        fields = parse_aprs_footer(footer, message_bytes)
                        if fields is not None:
                            fields[u"Message_Type"] = u"/"
                            fields.update(header_fields)
                            log_aprs_message(fields)
                            queue_display(fields, header=header, footer=footer)

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
                    if fields is not None:
                        fields[u"Message_Type"] = u";"
                        fields.update(header_fields)
                        log_aprs_message(fields)
                        queue_display(fields, header=header, footer=footer)

                except Exception, msg:
                    logger.info(u"7b Object Report Format")

                    try:
                        message_bytes = (1, 9, 1, 7, 8, 1, 9, 1, 7, 0)
                        fields = parse_aprs_footer(footer, message_bytes)
                        if fields is not None:
                            fields[u"Message_Type"] = u";"
                            fields.update(header_fields)
                            log_aprs_message(fields)
                            queue_display(fields, header=header, footer=footer)

                    except Exception, msg:  # else:
                        logger.info(u"7c %s" % msg)
                        message_bytes = (1, 9, 1, 7, 13, 43)
                        fields = parse_aprs_footer(footer, message_bytes)
                        if fields is not None:
                            fields[u"Message_Type"] = u";"
                            fields.update(header_fields)
                            log_aprs_message(fields)
                            queue_display(fields, header=header, footer=footer)

            # 8 aprslib >
            elif re.match(r"^>.*", footer, re.M | re.I):

                #
                # >- aprsfl.net/weather - New Port Richey WX
                try:
                    logger.info(u"8 Unknown")
                    fields = aprslib.parse(aprs_addresses)
                    if fields is not None:
                        fields[u"Message_Type"] = u">"
                        log_aprs_message(fields)
                        queue_display(fields, header=header, footer=footer)

                except Exception, msg:
                    logger.error(u"8 %s" % msg)

            # 9 aprslib :
            elif re.match(r"^:.*", footer, re.M | re.I):

                # __________________________________________________________________________________
                # :
                logger.info(u"9 Object Report Format")

                try:
                    fields = aprslib.parse(aprs_addresses)
                    if fields is not None:
                        fields[u"Message_Type"] = u":"
                        log_aprs_message(fields)
                        queue_display(fields, header=header, footer=footer)
                except Exception, msg:
                    logger.warn(u"9 %s" % msg)
                    message_bytes = (1, 9, 1, 67, 1, 0)
                    fields = parse_aprs_footer(footer, message_bytes)
                    if fields is not None:
                        fields[u"Message_Type"] = u":"
                        fields.update(header_fields)
                        log_aprs_message(fields)
                        queue_display(fields, header=header, footer=footer)

            # 10 aprslib `
            elif re.match(r"^`.*", footer, re.M | re.I):

                # __________________________________________________________________________________
                # MicE Format
                # `
                logger.info(u"10 eMic Format")
                fields = aprslib.parse(aprs_addresses)
                if fields is not None:
                    fields[u"Message_Type"] = u"MicE"
                    fields.update(header_fields)
                    nf = {k.title(): v for k, v in fields.items()}
                    log_aprs_message(nf)
                    queue_display(nf, header=header, footer=footer)

            else:
                # _____________________________________
                logger.debug(u"No match - %s" % footer)

        except Exception, msg:
            logger.error(u"decode_aprs_messages : %s" % msg)
            continue

    return message_counter


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
