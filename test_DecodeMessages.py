#!/usr/bin/env python
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


def get_data(message_type, func, rows=0):
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

    cursor = collection.find({u"Message_Type": {u'$eq': message_type}})  # .sort({u"_id": -1})

    for page in cursor[:rows]:
        if isinstance(page, dict):
            if func(page):
                success += 1
                results.append(page)
            else:
                failures.append(page)
                failure += 1

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
    logger.info(u"Sucess  : {}".format(success))
    logger.info(u"Failure : {}".format(failure))

    for f in failures[:show_rows]:
        m = f[u"Footer"]
        logger.error(u"    {}".format(m))

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
def test_ampersand(header):
    ret = True
    results = list()
    test_fields = list([u"Humidity", u"Pressure", u'Rain_1H', u"Rain_24H", u"Rain_Since_Midnight",
                        u"Temperature", u"Wind_Gust"])

    test_message = list()
    test_message.append(u"@022230z2813.12N/08214.30W_138/000g002t079r000p000P000Zephyrhills WX {UIV32N}")
    test_message.append(u"@170008z2831.07N/08142.92W_000/000g002t094r000p000P000h49b10150.DsVP")

    value_fields = list()
    value_fields.append([u"N/A", u"N/A", 0.0, 0.0, u"N/A", 79, 2])
    value_fields.append([49,     1015.0, 0.0, 0.0, 0.0,    94, 2])

    for m, footer in enumerate(test_message):
        logger.info(u"Footer         : .{}.".format(footer))
        logger.info(u"Header         : .{}.".format(header))
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
            logger.info(u"header_fields  : .{}.".format(header_fields))
            logger.info(u"aprs_addresses : .{}.".format(aprs_addresses))
            logger.info(u"fields : {}{}".format(fields, os.linesep))

            status = check_fields(value_fields[m], fields)

            if status is False:
                logger.warn(u"Failed transaction")

        except Exception as e:
            logger.warn(u"decode_aprs_messages {} {} {}".format(sys.exc_info()[-1].tb_lineno, type(e), e))
            ret = False

    assert ret is True


@pytest.mark.APRS
def test_ampersand_history():
    message_type = u"@a"
    ret = True
    rows = 100

    #              1            2             3           4            5          6
    # 0 123456 7 8901234 5 6 78901234 5 6 7 89012 3456 7890 1234 5678 9012 345 67890123456789
    # @ 311706 z 2815.27 N S 08139.28 W _ PHG74606/W3,FLn Davenport, Florida
    # @ 311657 z 2752.80 N S 08148.94 W _ PHG75506/W3,FLn-N Bartow, Florida
    # @ 074932 h 2833.70 N / 08120.29 W - Bob, Orlando, Florida
    # @ 010515 z 2815.27 N S 08139.28 W _ PHG74606/W3,FLn Davenport, Florida
    rem2 = u"^@\d{6}(h|z){1}\d{4}\.\d{2}(N|S){1}(/|S){1}\d{5}\.\d{2}(E|W)(_|#|-).*$"

    #              1            2            3            4            5          6
    # 0 123456 7 8901234 5 6 78901234 5 6 7890123 4567 8901 2345 6789 0123 45 67890123456789
    # @ 170008 z 2831.07 N / 08142.92 W _ 000/000 g002 t094 r000 p000 P000 h49 b10150 .DsVP
    # @ 011037 z 2815.56 N / 08241.26 W _ 142/000 g003 t055 r000 P000 p000 h94 b10211 - New Port Richey WX

    rem1 = u"^@\d{6}(h|z)\d{4}\.\d{2}(N|S)(/|S)\d{5}\.\d{2}(E|W)_\d{3}/\d{3}" \
           u"g\d{3}t\d{3}r\d{3}p\d{3}P\d{3}h\d{2}b\d{5}.+$"

    #              1            2            3           4            5           6
    # 0 123456 7 8901234 5 6 78901234 5 6 7890123 4567 8901 2345 6789 0123 456 789012 3456789
    # @ 080526 z 2815.27 N / 08139.28 W _ 136/002 g005 t075 r000 p057 P000 h00 b10073
    # @ 022230 z 2813.12 N / 08214.30 W _ 138/000 g002 t079 r000 p000 P000 Zephyrhills WX {UIV32N}
    rem0 = u"^@\d{6}(h|z){1}\d{4}\.\d{2}(N|S){1}(/|S){1}\d{5}\.\d{2}(E|W)_\d{3}/\d{3}" \
           u"g\d{3}t\d{3}r\d{3}p\d{3}P\d{3}h\d{2}b\d{5}$"

    def func(page):
        message = page[u"Footer"]

        logger.debug(u".{}.".format(message))
        if re.match(rem0, message):
            logger.info(u"0. Success : {}".format(message))
            return True
        else:
            if re.match(rem1, message):
                logger.info(u"1. Success : {}".format(message))
                return True
            else:
                if re.match(rem2, message):
                    logger.info(u"2. Success : {}".format(message))
                    return True
                else:
                    logger.info(u"3. Failure : {}".format(message))
                    return False

    success, failure, failures = get_data(message_type, func, rows=rows)
    state = status_response(success, failure, failures, show_rows=10)

    assert len(failures) == 0


@pytest.mark.APRS
def test_forward_slash_history():
    message_type = u"/a"
    #              1            2            3           4            5           6
    # 0 123456 7 8901234 5 6 78901234 5 6 7890123 4567 8901 2345 6789 0123 456 789012 3456789
    # / 062342 z 2803.50 N / 08146.10 W _ 210/000 g001t076r000P111h85b10072wVL1252")
    # / 311704 z 2757.15 N / 08147.20 W _ 103/008 g012t094r000p001P000h41b10183")
    # / 011851 z 2803.50 N / 08146.10 W _ 051/000 g006t096r000P000h45b10161wVL1252")

    rem0 = u"/\d{6}(z|h)\d{4}.+\d{2}(N|S){1}/\d{4}.+\d{2}(E|W){1}_\d{3}/\d{3}g\d{3}t[\d]{3}r\d{3}P\d{3}h\d{2}b\d{4}.*"
    rem1 = u"/\d{6}(z|h)\d{4}.+\d{2}(N|S){1}/\d{4}.+\d{2}(E|W){1}_\d{3}/\d{3}g\d{3}t[\d]{3}r\d{3}" \
           u"p\d{3}P\d{3}h\d{2}b\d{4}.*"
    rem2 = u"/\d{6}(z|h)\d{4}.+\d{2}(N|S){1}/\d{4}.+\d{2}(E|W){1}.+\d{3}/\d{3}.+"

    def func(page):
        message = page[u"Footer"]

        logger.debug(u".{}.".format(message))
        if re.match(rem0, message):
            logger.info(u"0. Success : {}".format(message))
            return True
        else:
            if re.match(rem1, message):
                logger.info(u"1. Success : {}".format(message))
                return True
            else:
                if re.match(rem2, message):
                    logger.info(u"2. Success : {}".format(message))
                    return True
                else:
                    logger.info(u"3. Failure : {}".format(message))
                    return False

    success, failure, failures = get_data(message_type, func, rows=100)
    state = status_response(success, failure, failures)
    assert len(failures) == 0


@pytest.mark.APRS
def test_equal_history():
    message_type = u"="
    #               1            2         3         4         5         6
    # 0 1234567 8 9 01234567 8 9 0123456789012345678901234567890123456789012 3456789
    # = 2835.63 N S 08118.08 W # PHG8250/DIGI_NED: OCCA Digi,www.w4mco.org,N2KIQ@arrl.net
    # = 2751.41 N / 08248.28 W _ PHG2160/NB9X Weather Station -FLPINSEMINOLE-285-<630>

    rows = 100

    rem0 = u"^=\d{4}\.\d{2}(N|S)(S|/|T|I)\d{5}\.\d{2}(E|W)(#|_|&|I|N|a|-).+"
    rem1 = u"=\d{4}.+\d{4}(N|S)(/|I)\d{4}.+\d{4}(W|E)/.+"
    rem2 = u"^=.+$"

    def func(page):
        message = page[u"Footer"]

        logger.debug(u".{}.".format(message))
        if re.match(rem0, message):
            logger.info(u"0. Success : {}".format(message))
            return True
        elif re.match(rem1, message):
            logger.info(u"1. Success : {}".format(message))
            return True
        elif re.match(rem2, message):
            logger.info(u"2. Successful Failure : {}".format(message))
            return False
        else:
            logger.info(u"3. Failure : {}".format(message))
            return False

    success, failure, failures = get_data(message_type, func, rows=100)
    state = status_response(success, failure, failures)
    assert len(failures) == 0


@pytest.mark.APRS
def test_semicolon_history():
    message_type = u";a"
    rows = 100

    # ;443.050- *111111z2832.38N\\08122.79Wy T103 R40m Skywarn w4mco.org
    # ;443.075+ *061653z2833.11N/08123.12WrCFRA
    # ;443.050- *111111z2832.38N\\08122.79Wy T103 R40m Skywarn w4mco.org
    # ;444.625_D*111111z2815.27N/08139.28Wr444.625MHz C127 R25m
    rem0 = u"^;\d{3}.+\d{3}[ +-].+\*\d{6}(z|h)\d{4}.\d{2}(N|S){1}.+\d{5}\.\d{2}(E|W){1}.+"
    rem1 = u""
    rem2 = u""

    def func(page):
        message = page[u"Footer"]

        logger.debug(u".{}.".format(message))
        if re.match(rem0, message):
            logger.info(u"0. Success : {}".format(message))
            return True
        elif re.match(rem1, message):
            logger.info(u"1. Success : {}".format(message))
            return True
        elif re.match(rem2, message):
            logger.info(u"2. Successful Failure : {}".format(message))
            return False
        else:
            logger.info(u"3 Failure : {}".format(message))
            return False

    success, failure, failures = get_data(message_type, func, rows=rows)
    state = status_response(success, failure, failures)
    assert len(failures) == 0


@pytest.mark.APRS
def test_exclamation_history():
    message_type = u"!a"
    rows = 10

    # !2749.10NS 08215.39W#PHG56304/W3,FLn Riverview, FL www.ni4ce.org (wind @ 810ft AGL)
    # !!0000009D02DB13E1279202B1--------00FF048D00000000
    rem0 = u"^!\d{4}\.\d{2}(N|S)(_|S|P)\d{5}\.\d{2}(E|W)(#|_)(.|,|/| \(\@).+"
    rem1 = u"^!\d{4}\.\d{2}(N|S)(_|S|P)\d{5}\.\d{2}(E|W).+"
    rem2 = u"^!\d{4}\.\d{2}(N|S)/\d{5}\.\d{2}(W|E)(#|_|).+"

    def func(page):
        message = page[u"Footer"]

        logger.debug(u".{}.".format(message))
        if re.match(rem0, message):
            logger.info(u"0. Success : {}".format(message))
            return True
        elif re.match(rem1, message):
            logger.info(u"1. Success : {}".format(message))
            return True
        elif re.match(rem2, message):
            logger.info(u"2. Success : {}".format(message))
            return True
        else:
            logger.info(u"4. Failure : {}".format(message))
            return False

    success, failure, failures = get_data(message_type, func, rows=rows)
    status_response(success, failure, failures)

    assert len(failures) == 0


if __name__ == u"__main__":

    test_message = list()
    header = u'AFSK1200: fm W4HEM-14 to APN391-0 via WC4PEM-15,WC4PEM-14,WIDE2-0 UI  pid=F0'

    test_ultw(header)

    test_underscore(header)

    test_ampersand(header)

    test_ampersand_history()

    test_forward_slash_history()

    test_equal_history()

    test_semicolon_history()

    test_exclamation_history()
