#!/usr/bin/env python
import cgitb
from ParseMessages import *
import aprslib
import pytest
from pymongo import *

from Logger import *

logger = setupLogging(__name__)
logger.setLevel(INFO)

MONGODB_SERVER = u"localhost"
MONGODB_PORT = 27017
MONGO_URI = u"mongodb://" + MONGODB_SERVER + u":%s" % MONGODB_PORT + u"/"
MONGODB_DB = u"local"
MONGODB_COLLECTION = u"Weather"

client = MongoClient(MONGO_URI)
db = client[MONGODB_DB]
collection = db[MONGODB_COLLECTION]

cgitb.enable(format=u"text")

message_types = list(
    [u"MicE", u"![ab]", u";[abc]", u"=[abc]", u"/[abc]", u"@[abc]", u"_[abc]", u"ultw", u">", u":[ab]", u"'", u"`"])

regular_expressions = list()
regular_expressions.append(u"^!\d{4}\.\d{2}(N|S)(_|S|P)\d{5}\.\d{2}(E|W)(#|_)(.|,|/| \(\@).+")
regular_expressions.append(u"^!\d{4}\.\d{2}(N|S)(_|S|P)\d{5}\.\d{2}(E|W).+")
regular_expressions.append(u"^!\d{4}\.\d{2}(N|S)/\d{5}\.\d{2}(W|E)(#|_|).+")

regular_expressions.append(u"^;\d{3}.+\d{3}[ +-_].+\*\d{6}(z|h)\d{4}.\d{2}(N|S){1}.+\d{5}\.\d{2}(E|W){1}.+$")
regular_expressions.append(u"^;\d{3}.+\d{3}[ +-_D]{1,2}\*\d{6}(z|h)\d{4}.\d{2}(N|S){1}.+\d{5}\.\d{2}(E|W){1}.+$")
regular_expressions.append(u"^;.+[*]\d{6}[z]\d{4}[.]\d{2}[NS]/\d{5}[\.]\d{2}[EW].+$")
regular_expressions.append(u"^;.+[*]\d{6}[z]\d{4}[.]\d{2}[nNsS].{1}\d{5}[.]\d{2}[eEwW].+$")

regular_expressions.append(u"^=\d{4}.{1}\d{2}(N|S)(S|/|T|I)\d{5}\.\d{2}(E|W)(#|_|&|I|N|a|-).+")
regular_expressions.append(u"^=\d{4}.{1}\d{4}(N|S)(/|I)\d{4}.+\d{4}(W|E)/.+")

regular_expressions.append(
    u"^/\d{6}(z|h)\d{4}\.\d{2}(N|S)/\d{5}\.\d{2}(E|W)_\d{3}/\d{3}g\d{3}t\d{3}r\d{3}p\d{3}P/d{3}h\d{2}b"
    u"\d{5}p\d{3}P\d{3}h\d{2}b\d{4}.*")
regular_expressions.append(
    u"^/\d{6}(z|h)\d{4}\.\d{2}(N|S)/\d{5}\.\d{2}(E|W)_\d{3}/\d{3}g\d{3}t\d{3}r\d{3}P\d{3}h\d{2}b\d{5}.*")
regular_expressions.append(u"^/\d{6}(z|h)\d{4}.+\d{2}(N|S){1}/\d{4}.+\d{2}(E|W){1}.+\d{3}/\d{3}.+")
regular_expressions.append(
    u"^/\d{6}(z|h)\d{4}\.\d{2}(N|S)/\d{5}\.\d{2}(E|W)_\d{3}/\d{3}g\d{3}t\d{3}r\d{3}p\d{3}P/d{3}h\d{2}b"
    u"\d{5}p\d{3}P\d{3}h\d{2}b\d{4}.*")

regular_expressions.append(u"^@\d{6}[h|z]\d{4}\.\d{2}[NS][/S]\d{5}\.\d{2}(E|W)[_#][|-_].+$")

regular_expressions.append(u"^@\d{6}[h|z]\d{4}\.\d{2}[N|S][/S]\d{5}\.\d{2}[E|W]_\d{3}[/]\d{3}" +
                           u"g\d{3}t\d{3}r\d{3}[pP]\d{3}[pP]\d{3}h\d{2}b\d{5}.+$")
regular_expressions.append(u"^@\d{6}[h|z]\d{4}\.\d{2}[NS][/S]\d{5}\.\d{2}[E|W]_\d{3}/\d{3}" +
                           u"g\d{3}t\d{3}r\d{3}p\d{3}P\d{3}h\d{2}b\d{5}.+$")


# ___________________________________________________________________________________________________________________


def get_data(message_type, func, rows=100):
    """
    This function will iterate through all messages for a given message type, and
    evaluate the regular expression inside the passed function. 
    This is doing closures in python.
    :param message_type: 
    :param func:
    :param rows: 
    :return: 
    """
    global collection
    success = 0
    failure = 0
    failures = list()
    results = list()

    if message_type is not None:
        cursor = collection.find({u"Message_Type": {u'$eq': message_type}}).sort("_id",
                                                                                 DESCENDING)  # sort({u"_id": -1})
    else:
        cursor = collection.find({u"Temperature": {u'$exists': u'false'}}).sort("_id", DESCENDING)  # sort({u"_id": -1})

    for page in cursor[:rows]:
        if isinstance(page, dict):
            try:
                if func(page):
                    success += 1
                    results.append(page)
                else:
                    failures.append(page)
                    failure += 1
            except Exception, msg:
                failures.append(page)
                failure += 1
                logger.error(u"msg  : {}".format(msg))
                logger.error(u"page : {}".format(page))

    return success, failure, failures


def check_fields(value_fields, test_fields):
    try:
        tl = test_fields.items()
        for m, f in enumerate(value_fields):
            value = value_fields[m]
            logger.debug(u".{}. : .{}. : .{}. : .{}.".format(value, type(value), f, type(f), f))

            if isinstance(f, (str, unicode)):
                w = f.strip()

            if isinstance(f, float):
                w = int(f)

            if isinstance(f, int):
                w = f

            if isinstance(value, (str, unicode)):
                e = value_fields[m].strip()

            if isinstance(value, float):
                e = int(value)

            if isinstance(value, int):
                e = value

            if e == w:
                logger.debug(u"True  \t {} : .{}. : .{}. : .{}. : .{}.".format(f, w, type(w), e, type(e), f))
            else:
                logger.info(u"False  \t {} : .{}. : .{}. : .{}. : .{}.".format(f, w, type(w), e, type(e), f))
    except Exception as e:
        logger.warn(u"decode_aprs_messages {} {} {}".format(sys.exc_info()[-1].tb_lineno, type(e), e))
        return False

    return True


def status_response(success, failure, failures, show_rows=100):
    mtd = dict()

    logger.info(
        u"____________________________________________________________________________________________________________")

    s = float(success)
    f = float(failure)

    logger.info(u"Sucess    : {}".format(s))
    logger.info(u"Failure   : {}".format(f))

    if s > 0:
        logger.info(u"Success % : {}".format((s / (s + f)) * 100.0))

    for q, f in enumerate(failures):
        m = f[u"Footer"][0]

        try:
            if m in mtd:
                if isinstance(mtd[m], list):
                    nl = list()
                    nl.append(m)
                    nl.append(q)
                    mtd[m].append(nl)
                else:
                    pass
            else:
                j = list()
                j.append(m)
                j.append(q)
                mtd[m] = j

        except KeyError, msg:
            pass

    if logger.getEffectiveLevel() == DEBUG:
        for z in mtd:
            a = len(z)
            b = z[0]

            logger.info(u"{}\t.{}.".format(a, b))

    logger.info(
        u"----------------------------------------------------------------------------------------------------------")

    if failure != 0:
        return False
    else:
        return True


# ___________________________________________________________________________________________________________________


@pytest.fixture(scope=u"module")
def header():
    header = u'AFSK1200: fm W4HEM-14 to APN391-0 via WC4PEM-15,WC4PEM-14,WIDE2-0 UI  pid=F0'
    return header


@pytest.mark.APRS
def test_ultw(header):
    logger.info(u"Test: test_ultw")

    ret = True
    ultw = list()
    failures = list()
    message_bytes = (5, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 0)
    test_fields = list([u"Barometer", u'Humidity', u"Message_Type", u"Temperature",
                        u"Time", u"Wind Direction", u"Wind Speed Peak", u"Zulu Time", ])

    value_fields = list()
    value_fields.append([1018.0, 100.0, u"$ULTW", 72.8, 80, u"ENE", 2.4, u"1:20"])
    value_fields.append([1017.2, 100.0, u"$ULTW", 72.3, 70.0, u"N", 0.0, u"1:10"])
    value_fields.append([1017.8, 100.0, u"$ULTW", 72.3, 1290.0, u"NE", 17.6, u"21:30"])
    value_fields.append([1015.9, 55, u"$ULTW", 88.7, 1130.9, 0, 8.6, u"18:50"])

    ultw.append(u"$ULTW0018006002D8821427C400038702000103E80099005000000001")
    ultw.append(u"$ULTW0000000002D3670F27BCFFFD8765000103E80099004600010000")
    ultw.append(u"$ULTW00B0004202D325ED27C200108935000103E80098050A0037006A")
    ultw.append(u"$ULTW005600E30377821427AFFFE987020001022F0099046A00000028")

    for n, message in enumerate(ultw):
        fields = parse_aprs_footer(message, message_bytes)
        fields[u"Message_Type"] = u"$ULTW"

        for m, f in enumerate(test_fields):
            value = value_fields[n][m]
            tf = fields[f]
            logger.debug(u".{}. : .{}. : .{}. : .{}.".format(value, type(value), tf, type(tf), f))

            if isinstance(tf, (str, unicode)):
                w = tf.strip()

            if isinstance(tf, float):
                w = int(tf)

            if isinstance(tf, int):
                w = tf

            if isinstance(value, (str, unicode)):
                e = value_fields[n][m].strip()

            if isinstance(value, float):
                e = int(value)

            if isinstance(value, int):
                e = value

            if e == w:
                logger.debug(u"True  \t {} : {} : {} : .{}. : .{}. : .{}. : .{}.".format(n, m, f, w,
                                                                                         type(w), e, type(e), f))
            else:

                logger.info(u"False  \t {} : {} : {} : .{}. : .{}. : .{}. : .{}.".format(n, m, f, w,
                                                                                         type(w), e, type(e), f))
                failures.append(u"{} : {} : {} : {}".format(m, n, e, w))

    assert len(failures) == 0


@pytest.mark.APRS
def test_underscore(header):
    logger.info(u"Test: test_underscore")
    failures = list()
    test_fields = list([u"Humidity", u"Pressure", u'Rain_1H', u"Rain_24H", u"Rain_Since_Midnight",
                        u"Temperature", u"Wind_Direction", u"Wind_Gust", u"Wind_Speed"])

    value_fields = list()
    value_fields.append([64, 1016.0, 0, 21.844, 0.0, 30.0, 359, 0.0, 0.0])
    value_fields.append([99, 1018.2, 0.0, 21.844, 8.89, 23.8, 359, 0, 0])

    test_message = list()
    test_message.append(u"_05311550c359s000g000t086r000p086P000h64b10160tU2k")
    test_message.append(u"_05312040c359s000g000t075r000p086P035h99b10182tU2k")

    for m, footer in enumerate(test_message):
        logger.debug(u"Footer         : .{}.".format(footer))
        logger.debug(u"Header         : .{}.".format(header))

        header_fields, aprs_addresses = parse_aprs_header(header, footer)
        logger.debug(u"header_fields  : .{}.".format(header_fields))
        logger.debug(u"aprs_addresses : .{}.".format(aprs_addresses))

        fields = aprslib.parse(aprs_addresses)
        fields[u"Message_Type"] = u"_"
        fields.update(header_fields)

        nf = {k.title(): v for k, v in fields[u"weather"].items()}
        del fields[u"weather"]
        nfa = {k.title(): v for k, v in nf.items()}
        cf = check_fields(value_fields[m], nfa)

        assert cf is True


@pytest.mark.APRS
def test_underscore_history(rows=100):
    logger.info(u"Test: test_underscore_history")
    message_type = u"_a"
    ret = True

    # 123456789 0123 4567 8901 2345 6789 0123 4567 890 123456 78901234567890123456789
    # _05311550 c359 s000 g000 t086 r000 p086 P000 h64 b10160 tU2k
    # _05312040 c359 s000 g000 t075 r000 p086 P035 h99 b10182 tU2k
    # _06051349 c359 s000 g000 t081 r000 p037 P023 h89 b10084 tU2k

    rem = list()
    rem.append(u"^_\d{8}c\d{3}s\d{3}g\d{3}t\d{3}r\d{3}p\d{3}P\d{3}h\d{2}b\d{5}.{4}")

    def func(page):
        message = page[u"Footer"]

        for m in rem:
            logger.debug(u".{}.".format(message))
            if re.match(m, message):
                logger.debug(u"Success : {}".format(message))
                return True

        logger.info(u"Failure : {}".format(message))
        return False

    success, failure, failures = get_data(message_type, func, rows=rows)
    state = status_response(success, failure, failures, show_rows=10)

    assert len(failures) == 0


@pytest.mark.APRS
def test_ampersand(header):
    logger.info(u"Test: test_ampersand")
    ret = True
    results = list()
    test_fields = list([u"Humidity", u"Pressure", u'Rain_1H', u"Rain_24H", u"Rain_Since_Midnight",
                        u"Temperature", u"Wind_Gust"])

    test_message = list()
    test_message.append(u"@022230z2813.12N/08214.30W_138/000g002t079r000p000P000Zephyrhills WX {UIV32N}")
    test_message.append(u"@170008z2831.07N/08142.92W_000/000g002t094r000p000P000h49b10150.DsVP")

    value_fields = list()
    value_fields.append([u"N/A", u"N/A", 0.0, 0.0, u"N/A", 79, 2])
    value_fields.append([49, 1015.0, 0.0, 0.0, 0.0, 94, 2])

    for m, footer in enumerate(test_message):
        logger.debug(u"Footer         : .{}.".format(footer))
        logger.debug(u"Header         : .{}.".format(header))
        fields = dict()

        try:
            if footer[15] == u"N" and footer[25] == u"W":
                fields[u"Time"] = footer[1:6]
                fields[u"Latitude"] = footer[8:10] + u"." + footer[10:12] + footer[13:16]

                if footer[17] == u"0":
                    fields[u"Longitude"] = footer[18:20] + u"." + footer[19:21] + footer[23:26]
                else:
                    fields[u"Longitude"] = footer[17:19] + u"." + footer[19:21] + footer[23:26]

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

            header_fields, aprs_addresses = parse_aprs_header(header, footer)
            logger.debug(u"header_fields  : .{}.".format(header_fields))
            logger.debug(u"aprs_addresses : .{}.".format(aprs_addresses))
            logger.debug(u"fields : {}{}".format(fields, os.linesep))

            status = check_fields(value_fields[m], fields)

            if status is False:
                logger.warn(u"Failed transaction")

        except Exception as e:
            logger.warn(u"decode_aprs_messages {} {} {}".format(sys.exc_info()[-1].tb_lineno, type(e), e))
            ret = False

    assert ret is True


@pytest.mark.APRS
def test_ampersand_history(rows=100):
    logger.info(u"Test: test_ampersand_history")
    message_type = u"@a"
    ret = True
    rem = list()

    #              1            2             3           4            5          6
    # 0 123456 7 8901234 5 6 78901234 5 6 7 89012 3456 7890 1234 5678 9012 345 67890123456789
    # @ 311706 z 2815.27 N S 08139.28 W _ PHG74606/W3,FLn Davenport, Florida
    # @ 311657 z 2752.80 N S 08148.94 W _ PHG75506/W3,FLn-N Bartow, Florida
    # @ 074932 h 2833.70 N / 08120.29 W - Bob, Orlando, Florida
    # @ 010515 z 2815.27 N S 08139.28 W _ PHG74606/W3,FLn Davenport, Florida
    rem.append(u"^@\d{6}(h|z){1}\d{4}\.\d{2}(N|S){1}(/|S){1}\d{5}\.\d{2}(E|W)(_|#|-).*$")

    #              1            2            3            4            5          6
    # 0 123456 7 8901234 5 6 78901234 5 6 7890123 4567 8901 2345 6789 0123 45 67890123456789
    # @ 170008 z 2831.07 N / 08142.92 W _ 000/000 g002 t094 r000 p000 P000 h49 b10150 .DsVP
    # @ 011037 z 2815.56 N / 08241.26 W _ 142/000 g003 t055 r000 P000 p000 h94 b10211 - New Port Richey WX

    rem.append(u"^@\d{6}(h|z)\d{4}\.\d{2}(N|S)(/|S)\d{5}\.\d{2}(E|W)_\d{3}/\d{3}" \
               u"g\d{3}t\d{3}r\d{3}p\d{3}P\d{3}h\d{2}b\d{5}.+$")

    #              1            2            3           4            5           6
    # 0 123456 7 8901234 5 6 78901234 5 6 7890123 4567 8901 2345 6789 0123 456 789012 3456789
    # @ 080526 z 2815.27 N / 08139.28 W _ 136/002 g005 t075 r000 p057 P000 h00 b10073
    # @ 022230 z 2813.12 N / 08214.30 W _ 138/000 g002 t079 r000 p000 P000 Zephyrhills WX {UIV32N}
    rem.append(u"^@\d{6}(h|z){1}\d{4}\.\d{2}(N|S){1}(/|S){1}\d{5}\.\d{2}(E|W)_\d{3}/\d{3}" \
               u"g\d{3}t\d{3}r\d{3}p\d{3}P\d{3}h\d{2}b\d{5}$")

    def func(page):
        message = page[u"Footer"]

        for m in rem:
            logger.debug(u".{}.".format(message))
            if re.match(m, message):
                logger.debug(u"Success : {}".format(message))
                return True

        logger.info(u"Failure : {}".format(message))
        return False

    success, failure, failures = get_data(message_type, func, rows=rows)
    state = status_response(success, failure, failures, show_rows=10)

    assert len(failures) == 0


@pytest.mark.APRS
def test_forward_slash_history(rows=100):
    logger.info(u"Test: test_forward_slash_history")
    message_type = u"/a"

    #              1            2            3           4            5           6
    # 0 123456 7 8901234 5 6 78901234 5 6 7890123 4567 8901 2345 6789 0123 456 789012 3456789
    # / 062342 z 2803.50 N / 08146.10 W _ 210/000 g001 t076 r000 P111 h85 b10072 wVL1252")
    # / 311704 z 2757.15 N / 08147.20 W _ 103/008 g012 t094 r000 p001 P000 h41 b10183")
    # / 011851 z 2803.50 N / 08146.10 W _ 051/000 g006 t096 r000 P000 h45 b10161 wVL1252")

    rem = list()
    rem.append(
        u"^/\d{6}(z|h)\d{4}\.\d{2}(N|S)/\d{5}\.\d{2}(E|W)_\d{3}/\d{3}g\d{3}t\d{3}r\d{3}p\d{3}P/d{3}h\d{2}b\d{5}p\d{3}P\d{3}h\d{2}b\d{4}.*")
    rem.append(u"^/\d{6}(z|h)\d{4}\.\d{2}(N|S)/\d{5}\.\d{2}(E|W)_\d{3}/\d{3}g\d{3}t\d{3}r\d{3}P\d{3}h\d{2}b\d{5}.*")
    rem.append(u"^/\d{6}(z|h)\d{4}.+\d{2}(N|S){1}/\d{4}.+\d{2}(E|W){1}.+\d{3}/\d{3}.+")
    rem.append(
        u"^/\d{6}(z|h)\d{4}\.\d{2}(N|S)/\d{5}\.\d{2}(E|W)_\d{3}/\d{3}g\d{3}t\d{3}r\d{3}p\d{3}P/d{3}h\d{2}b\d{5}p\d{3}P\d{3}h\d{2}b\d{4}.*")

    def func(page):
        message = page[u"Footer"]

        for m in rem:
            logger.debug(u".{}.".format(message))
            if re.match(m, message):
                logger.debug(u"Success : {}".format(message))
                return True

        logger.info(u"Failure : {}".format(message))
        return False

    success1, failure1, failures1 = get_data(u"/a", func, rows=rows)
    success2, failure2, failures2 = get_data(u"/b", func, rows=rows)
    success3, failure3, failures3 = get_data(u"/c", func, rows=rows)

    success = success1 + success2 + success3
    failure = failure1 + failure2 + failure3
    failures = failures1 + failures2 + failures3

    state = status_response(success, failure, failures, show_rows=10)

    assert len(failures) == 0


@pytest.mark.APRS
def test_equal_history(rows=100):
    logger.info(u"Test: test_equal_history")
    message_type = u"="

    #               1            2         3         4         5         6
    # 0 1234567 8 9 01234567 8 9 0123456789012345678901234567890123456789012 3456789
    # = 2835.63 N S 08118.08 W # PHG8250/DIGI_NED: OCCA Digi,www.w4mco.org,N2KIQ@arrl.net
    # = 2751.41 N / 08248.28 W _ PHG2160/NB9X Weather Station -FLPINSEMINOLE-285-<630>
    # = 2749.32 N / 08244.16 W _ 084/000g000t082r000P000p000h67b10176XU2k

    rem = list()
    rem.append(u"^=\d{4}.{1}\d{2}(N|S)(S|/|T|I)\d{5}\.\d{2}(E|W)(#|_|&|I|N|a|-).+")
    rem.append(u"^=\d{4}.{1}\d{4}(N|S)(/|I)\d{4}.+\d{4}(W|E)/.+")

    def func(page):
        message = page[u"Footer"]

        for m in rem:
            logger.debug(u".{}.".format(message))
            if re.match(m, message):
                logger.debug(u"Success : {}".format(message))
                return True

        logger.info(u"Failure : {}".format(message))
        return False

    success, failure, failures = get_data(message_type, func, rows=rows)
    state = status_response(success, failure, failures)

    assert len(failures) == 0


@pytest.mark.APRS
def test_semicolon_history(rows=100):
    logger.info(u"Test: test_semicolon_history")
    message_type = u";a"

    #               1           2              3           4         5         6
    # 0 1234567 8 9 012345 6 7890123 4 5  678901234 5 678901234567890123456789012 3456789
    # ; 443.050 - * 111111 z 2832.38 N \\ 08122.79 W y T103 R40m Skywarn w4mco.org
    # ; 443.075 + * 061653 z 2833.11 N /  08123.12 W r CFRA
    # ; 443.050 - * 111111 z 2832.38 N \\ 08122.79 W y  T103 R40m Skywarn w4mco.org
    # ; W1KFR-DMR * 121708 z 3049.66 N / 08144.44  W r 444.625 (+) Color Code 3
    # ; CMC       * 012256 z 3046.86 N / 08136.85  W h SEGRMC Camden Campus
    # ; HamCation * 120114 z 2833.31 N \ 08126.26 W h 2/09 thru 2/11 HamCation.com W4MCO

    rem = list()
    rem.append(u"^;\d{3}.+\d{3}[ +-_].+\*\d{6}(z|h)\d{4}.\d{2}(N|S){1}.+\d{5}\.\d{2}(E|W){1}.+$")
    rem.append(u"^;\d{3}.+\d{3}[ +-_D]{1,2}\*\d{6}(z|h)\d{4}.\d{2}(N|S){1}.+\d{5}\.\d{2}(E|W){1}.+$")
    rem.append(u"^;.+[*]\d{6}[z]\d{4}[.]\d{2}[NS]/\d{5}[\.]\d{2}[EW].+$")
    rem.append(u"^;.+[*]\d{6}[z]\d{4}[.]\d{2}[nNsS].{1}\d{5}[.]\d{2}[eEwW].+$")

    def func(page):
        message = page[u"Footer"]

        for n, m in enumerate(rem):
            logger.debug(u".{}.".format(message))
            if re.match(m, message):
                logger.debug(u"Success : {}".format(message))
                return True

        logger.info(u"No Match : {}".format(n))

        return False

    success, failure, failures = get_data(message_type, func, rows=rows)
    state = status_response(success, failure, failures)

    assert len(failures) == 0


@pytest.mark.APRS
def test_exclamation_history(rows=100):
    logger.info(u"Test: test_exclamation_history")
    message_type = u"!a"

    # !2749.10NS 08215.39W#PHG56304/W3,FLn Riverview, FL www.ni4ce.org (wind @ 810ft AGL)
    # !!0000009D02DB13E1279202B1--------00FF048D00000000

    rem = list()
    rem.append(u"^!\d{4}\.\d{2}(N|S)(_|S|P)\d{5}\.\d{2}(E|W)(#|_)(.|,|/| \(\@).+")
    rem.append(u"^!\d{4}\.\d{2}(N|S)(_|S|P)\d{5}\.\d{2}(E|W).+")
    rem.append(u"^!\d{4}\.\d{2}(N|S)/\d{5}\.\d{2}(W|E)(#|_|).+")

    def func(page):
        message = page[u"Footer"]

        for m in rem:
            logger.debug(u".{}.".format(message))
            if re.match(m, message):
                logger.debug(u"0. Success : {}".format(message))
                return True

        logger.info(u"3. Failure : {}".format(message))
        return False

    success, failure, failures = get_data(message_type, func, rows=rows)
    status_response(success, failure, failures)

    assert len(failures) == 0


@pytest.mark.APRS
def test_MicE(header, footer, rows=100):
    header_fields, aprs_addresses = parse_aprs_header(header, footer)

    try:
        logger.info(u"10 eMic Format")
        fields = aprslib.parse(aprs_addresses)
        fields[u"Message_Type"] = u"MicE"
        fields[u"longitude"] = u"{:6.2f}W".format(fields[u"longitude"])
        fields[u"latitude"] = u"{:6.2f}N".format(fields[u"latitude"])
        fields.update(header_fields)

    except Exception, msg:
        logger.error(u"Parse Error: {}".format(msg))


def test_messages(rows=100):
    logger.info(u"Test: test_messages")
    global regular_expressions
    message_type = None
    mtf = dict()

    def func(page):
        footer = page[u"Footer"]
        header = page[u"Header"]
        message_type = footer[0]

        for n, m in enumerate(regular_expressions):
            logger.debug(u".{}.".format(footer))
            if re.match(m, footer, re.M | re.I):
                logger.debug(u"{}. Success : {}\t{}".format(n, footer, m))
                return True

        return False

    success, failure, failures = get_data(message_type, func, rows=rows)

    status_response(success, failure, failures, show_rows=rows)


if __name__ == u"__main__":

    try:
        if False:
            test_messages(rows=10000)

        else:
            header = u'AFSK1200: fm W4HEM-14 to APN391-0 via WC4PEM-15,WC4PEM-14,WIDE2-0 UI  pid=F0'

            footer = u"""`n-.l{.>/`"4b}_%"""
            test_MicE(header, footer, rows=0)

            footer = u"""`mIHq^`>/'"4@}|#u&0(4|!wal!|3"""
            test_MicE(header, footer, rows=0)

            test_ultw(header)

            test_underscore(header)

            test_ampersand(header)

            test_ampersand_history(rows=10000)

            test_forward_slash_history(rows=10000)

            test_underscore_history(rows=10000)

            test_equal_history(rows=10000)

            test_semicolon_history(rows=10000)

            test_exclamation_history(rows=10000)

    except KeyboardInterrupt:
        logger.info(u"Goodbye...")
