#!/usr/bin/env python
import re
from datetime import datetime, timedelta
from ListAngle import *
from Logger import *
logger = setupLogging(__name__)
logger.setLevel(INFO)


def parse_aprs_header(header, footer, n=0):
    """
    Parse APRS Headers
    :param header:
    :param footer:
    :param n:
    :return:
    """
    header_fields = None
    aprs_addresses = None

    try:
        # fm WC4PEM-10 to APMI06-0 via WC4PEM-14,WIDE2-1 UI  pid=F0
        addresses = header.split(u" ")
        fm = addresses[2]
        to = addresses[4]
        path = addresses[6]

        if path is None or not (len(path) > 1):
            via = addresses[5]
            logger.error(u"via is {0!r}".format(via))

        # M0XER-4>APRS64,TF3RPF,WIDE2*,qAR,TF3SUT-2
        aprs_addresses = u"{0}>{1},{2}:{3}".format(fm, to, path, footer)
        message = u"{0!r} ->{1!r}-> {2!r}".format(fm, path, to)
        logger.debug(message)

        logger.debug(u"%3d [%s]" % (n, header[10:]))
        logger.debug(u"    [%s]" % footer)

        header_fields = {u"From": fm, u"To": to, u"Path": path}
    except Exception, msg:
        logger.error(u"%s" % msg)

    return header_fields, aprs_addresses


def parse_aprs_footer(footer, msg_bytes):
    """
    Parse APRS Footer
    :param footer:
    :param msg_bytes:
    :return:
    """
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


def parse_wind_direction(direction):
    global letter_angle
    angle = 0

    logger.debug(u"Wind Direction (n) : {} : {}".format(direction, type(direction)))

    try:
        if isinstance(direction, (str, unicode)):
            d = int(direction)
        elif isinstance(direction, float):
            d = int(direction)
        else:
            d = direction

        try:
            for dn in list_angle:
                if dn[0] < d < dn[1]:
                    angle = dn[2]
                    logger.debug(u"Found - %4.1f-%4.1f \t %s" % (dn[0], dn[1], dn[2]))
                    break

        except Exception, msg:
            logger.error(u"%s" % msg)

        logger.debug(u"Wind Direction (angle) : {} ".format(angle))
    except Exception, msg:
        pass

    return angle


def parse_ULTW_message(field, msg, scale=1.0):
    u"""
    function to convert hex to the proper value
    :param field:
    :param msg:
    :param scale:
    :return:
    """
    fld = None
    try:
        # if field <> u"----":
        if re.match(r"^[0-9A-Za-z]{4}", field, re.M | re.I):
            fld = int(u"0x" + field, 16) * scale
            logger.debug(u"%7.2f : %s" % (fld, msg))
    except Exception, msg:
        logger.warn(u"%s : %s" % (msg, field))

    return fld


def parse_Zulu_EDT(pt):
    """
    Convert time from Zulu time
    :param pt:
    :return:
    """
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


def parse_days(days):
    """
    Parse out data from string
    :param days:
    :return:
    """
    year = int(datetime.now().strftime(u'%Y'))
    n = datetime(day=1, month=1, year=year)
    EndDate = n + timedelta(days=days)

    return EndDate.strftime(u'%Y/%m/%d')


def parse_weather_message(msg):
    """
    :param msg:
    :return:
    """

    wm = dict()
    wmessage = None

    try:
        # Begin displaying messages
        for k, v in sorted(msg.items(), reverse=False):
            if k in [u"Barometer", u"Barometric Pressure", u"Temperature", u"Humidity", ]:
                wm[k] = v

        temp = u"{}".format(wm[u"Temperature"]) if u"Temperature" in wm else u"."
        humidity = u"{}".format(wm[u"Humidity"]) if u"Humidity" in wm else u"."
        pressure = u"{}".format(wm[u"Barometer"]) if u"Barometer" in wm else wm[u"Barometric Pressure"]

        wmessage = u"{0:2}F {1:2}% {2:6}".format(temp, humidity, pressure)
        logger.debug(u"{}".format(wmessage))

    except KeyError, msg:
        logger.debug(u"{}".format(msg))

    if wmessage == u"":
        return None
    else:
        return wmessage


def parse_aprs_fields(fields):
    """
    Create a dict of decoded fields
    :param fields:
    :return:
    """
    weather = [u"@", u"=", u"_", u"/", u"!"]
    fld = dict()
    n = 0

    # Weather Messages
    if fields[0] in weather:
        fld[u"Message_Type"] = fields[0]
        for n, field in enumerate(fields[1:]):
            logger.debug(u"%03d : %s" % (n, field))

            try:
                if field[0] == u"t":
                    n = 1
                    logger.debug(u"%6d : [ Temperature ]" % int(field[1:]))
                    fld[u"Temperature"] = int(field[1:])

                elif field[0] == u"h":
                    n = 2
                    logger.debug(u"%6d : [ Humidity ]" % int(field[1:]))
                    fld[u"Humidity"] = int(field[1:])

                elif field[0] == u"r":
                    n = 4
                    if len(field[1:]) > 2:
                        fv = int(field[1:]) * 0.01
                        logger.debug(u"%6.1f : [ Rainfall in the last hour ]" % fv)
                        fld[u"Rainfall in the last hour"] = fv

                elif field[0] == u"P":
                    n = 5
                    fv = int(field[1:]) * 0.01
                    logger.debug(u"%6.1f : [ Rainfall in the last 24 hour]" % fv)
                    fld[u"Rainfall in the last 24 hour"] = fv

                elif field[0] == u"p":
                    n = 6
                    fv = int(field[1:]) * 0.01
                    logger.debug(u"%6.1f : [ Rainfall since midnight ]" % fv)
                    fld[u"Rainfall since midnight"] = fv

                elif field[0] == u"b":
                    n = 7
                    fv = float(field[1:]) * 0.1
                    logger.debug(u"%6.1f : [ Barometric Pressure] " % fv)
                    # fld[u"Barometric Pressure"] = fv
                    fld[u"Barometer"] = fv

                elif field[0] == u"c":
                    n = 8
                    fv = int(field[1:])
                    angle = parse_wind_direction(fv)
                    logger.debug(u"%s : [ Wind Direction ]" % angle)
                    fld[msg] = parse_ULTW_message(angle, msg)
                    fld[u"Wind Direction"] = angle

                elif field[0] == u"s":
                    n = 9
                    fv = int(field[1:])
                    logger.debug(u"%6d : [ Sustained Wind Speed ]" % fv)
                    fld[u"Sustained wind speed"] = fv

                elif field[0] == u"g":
                    n = 10
                    fv = int(field[1:])
                    logger.debug(u"%6d : [ Wind Gust]" % fv)
                    fld[u"Wind Gust"] = fv

                elif field[-1:] in (u"N", u"S"):  # and len(field) > 2:
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

        return fld

    # ULTW Messages
    elif fields[0][:5] == u"$ULTW":
        # $ULTW 0000 0000 01FF 0004 27C7 0002 CCD3 0001 026E 003A 050F 0004 0000
        fld[u"Message_Type"] = u"ULTW"

        try:
            n = 20
            m = u"Wind Speed Peak over last 5 min (0_1 kph increments)"
            msg = u"Wind Speed Peak"
            fld[msg] = parse_ULTW_message(fields[1], msg, scale=0.1)

            n = 21
            m = u"Wind Direction of Wind Speed Peak (0-255)"
            msg = u"Wind Direction"
            fa = fields[2]
            angle = parse_wind_direction(fa)
            fld[msg] = angle

            n = 22
            m = u"Current Outdoor Temp (0_1 deg F increments)"
            msg = u"Temperature"
            fld[msg] = parse_ULTW_message(fields[3], msg, scale=0.1)

            n = 23
            msg = u"Rain Long Term Total (0_01 in increments)"
            # fld[msg] = parse_ULTW_Message(fields[4], msg, scale=0.01)

            n = 24
            m = u"Current Barometer (0_1 mbar increments)"
            msg = u"Barometer"
            fld[msg] = parse_ULTW_message(fields[5], msg, scale=0.1)

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
            fld[msg] = parse_ULTW_message(fields[9], msg, scale=0.1)

            n = 29
            m = u"Date (day of year since January 1)"
            # msg = u"Date"
            # fld[msg] = parse_ULTW_Message(fields[10], msg)

            n = 30
            msg2 = u"Zulu Time"
            pzt = parse_Zulu_EDT(fields[11])
            fld[msg2] = pzt
            m = u"Time (minute of day)"
            msg = u"Time"
            fld[msg] = parse_ULTW_message(fields[11], msg)

            n = 31
            msg = u"Today's Rain Total (0_01 inch increments)"
            # fld[msg] = parse_ULTW_Message(fields[12], msg, scale=0.01)

            n = 32
            msg = u"Minute Wind Speed Average (0_1kph increments)"
            # fld[msg] = parse_ULTW_Message(fields[13], msg, scale=0.1)

            return fld

        except KeyError, msg:
            logger.debug(u"$ULTW[%d] Error : %s" % (n, msg))

    # Unknown Message
    else:
        logger.debug(u"Unknown")
        return None

if __name__ == u"__main__":
    pass
