#!/usr/bin/env python
from ParseMessages import *
import aprslib

from Logger import *
logger = setupLogging(__name__)
logger.setLevel(DEBUG)


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


def test_ultw(header):

    ret = True
    ultw = list()
    message_bytes = (5, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 0)
    test_fields = list([u"Barometer", u'Humidity', u"Message_Type", u"Temperature",
                        u"Time", u"Wind Direction", u"Wind Speed Peak", u"Zulu Time", ])

    value_fields = list()
    value_fields.append([1018.0, 100.0, u"$ULTW", 72.8, 80, u"ENE", 2.4, u"1:20"])
    value_fields.append([1017.2, 100.0, u"$ULTW", 72.3, 70.0, u"N", 0.0, u"!:10"])
    value_fields.append([1017.8, 100.0, u"$ULTW", 72.3, 1290.0, u"NE", 17.6, u"21:30"])
    value_fields.append([1015.9, 55.9, u"$ULTW", 88.7, 55.9, u"NE", 8.6, u"10:06"])

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
                logger.debug(u"True  \t {} : .{}. : .{}. : .{}. : .{}.".format(f, w, type(w), e, type(e), f))
            else:
                logger.info(u"False  \t {} : .{}. : .{}. : .{}. : .{}.".format(f, w, type(w), e, type(e), f))

    return ret


def test_underscore(header):

    ret = True

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

    return ret


def test_ampersand(header):

    ret = True

    test_fields = list([u"Humidity", u"Pressure", u'Rain_1H', u"Rain_24H", u"Rain_Since_Midnight",
                        u"Temperature", u"Wind_Gust"])

    test_message = list()
    test_message.append(u"@022230z2813.12N/08214.30W_138/000g002t079r000p000P000Zephyrhills WX {UIV32N}")
    test_message.append(u"@170008z2831.07N/08142.92W_000/000g002t094r000p000P000h49b10150.DsVP")

    #              1            2             3           4            5          6
    # 0 123456 7 8901234 5 6 78901234 5 6 7 89012 3456 7890 1234 5678 9012 345 67890123456789
    # @ 022230 z 2813.12 N / 08214.30 W _ 138/000 g002 t079 r000 p000 P000 Zephyrhills WX {UIV32N}
    # @ 170008 z 2831.07 N / 08142.92 W _ 000/000 g002 t094 r000 p000 P000 h49 b10150 .DsVP

    # test_message.append(u"@311706z2815.27NS08139.28W_PHG74606/W3,FLn Davenport, Florida")
    # test_message.append(u"@311657z2752.80NS08148.94W_PHG75506/W3,FLn-N Bartow, Florida")
    # test_message.append(u"@095148h2835.66N/08118.09Wo Orange County ARES")

    #              1            2             3           4            5          6
    # 0 123456 7 8901234 5 6 78901234 5 6 7 89012 3456 7890 1234 5678 9012 345 67890123456789
    # @ 311706 z 2815.27 N S 08139.28 W _ PHG74606/W3,FLn Davenport, Florida
    # @ 311657 z 2752.80 N S 08148.94 W _ PHG75506/W3,FLn-N Bartow, Florida
    # @ 095148h2835.66 N / 08118.09 W o Orange County ARES

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
                fields[u"Latitude"] = footer[8:16]
                fields[u"Longitude"] = footer[17:26]

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

            status = check_fields(value_fields[m], fields)

            if status is False:
                logger.warn(u"Failed transaction")

        except Exception as e:
            logger.warn(u"decode_aprs_messages {} {} {}".format(sys.exc_info()[-1].tb_lineno, type(e), e))
            ret = False

    return ret


if __name__ == u"__main__":

    header = u'AFSK1200: fm W4HEM-14 to APN391-0 via WC4PEM-15,WC4PEM-14,WIDE2-0 UI  pid=F0'

    # test_ultw(header)

    # test_underscore(header)

    # test_ampersand(header)

    test_message = list()

    s = u"=2816.97NS08242.70W#PHG74326/W3 Digi, Port Richey, FL aprsfl.net"
    rem = u"^=\d{4}.\d{2}[NS]{1}.+\d{4}.\d{2}[EW]{1}.+"

    if re.match(rem, s, re.M):
        t = True
        logger.debug(u"{}".format(t))

    # Skip for now
    test_message.append(u"/062342z2803.50N/08146.10W_210/000g001t076r000P111h85b10072wVL1252")
    test_message.append(u"/311704z2757.15N/08147.20W_103/008g012t094r000p001P000h41b10183")
    test_message.append(u"/011851z2803.50N/08146.10W_051/000g006t096r000P000h45b10161wVL1252")

    # Skip for now
    test_message.append(u"!2749.10NS08215.39W#PHG56304/W3,FLn Riverview, FL www.ni4ce.org (wind @ 810ft AGL)")
    test_message.append(u"=2835.63NS08118.08W#PHG8250/DIGI_NED: OCCA Digi,www.w4mco.org,N2KIQ@arrl.net")
    test_message.append(u"=2751.41N/08248.28W_PHG2160/NB9X Weather Station -FLPINSEMINOLE-285-<630>")
    test_message.append(u";145.650*051916z2749.31N/08244.16Wr/A=000025AA/Cert-Node 273835")

