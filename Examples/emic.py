#!/usr/bin/env python
import math
import re
from math import log, ceil
from re import findall

from Logger import *

logger = setupLogging(__name__)
logger.setLevel(INFO)

__all__ = [u'parse_mice', ]

# Mic-e message type table

MTYPE_TABLE_STD = {
    u"111": u"M0: Off Duty",
    u"110": u"M1: En Route",
    u"101": u"M2: In Service",
    u"100": u"M3: Returning",
    u"011": u"M4: Committed",
    u"010": u"M5: Special",
    u"001": u"M6: Priority",
    u"000": u"Emergency",
}

MTYPE_TABLE_CUSTOM = {
    u"111": u"C0: Custom-0",
    u"110": u"C1: Custom-1",
    u"101": u"C2: Custom-2",
    u"100": u"C3: Custom-3",
    u"011": u"C4: Custom-4",
    u"010": u"C5: Custom-5",
    u"001": u"C6: Custom-6",
    u"000": u"Emergency",
}

def to_decimal(text):
    """
    Takes a base91 char string and returns decimal
    """

    if not isinstance(text, (str, unicode)):
        raise TypeError(u"expected str or unicode, %s given" % type(text))

    if findall(r"[\x00-\x20\x7c-\xff]", text):
        raise ValueError(u"invalid character in sequence")

    text = text.lstrip('!')
    decimal = 0
    length = len(text) - 1
    for i, char in enumerate(text):
        decimal += (ord(char) - 33) * (91 ** (length - i))

    return decimal if text != '' else 0

def from_decimal(number, width=1):
    """
    Takes a decimal and returns base91 char string.
    With optional parameter for fix with output
    """
    text = []

    if not isinstance(number, (int, long)):
        raise TypeError(u"Expected number to be int, got %s", type(number))
    elif not isinstance(width, (int, long)):
        raise TypeError(u"Expected width to be int, got %s", type(number))
    elif number < 0:
        raise ValueError(u"Expected number to be positive integer")
    elif number > 0:
        max_n = ceil(log(number) / log(91))

        for n in xrange(int(max_n), -1, -1):
            quotient, number = divmod(number, 91**n)
            text.append(chr(33 + quotient))

    return "".join(text).lstrip('!').rjust(max(1, width), '!')

def parse_comment_telemetry(text):
    """
    Looks for base91 telemetry found in comment field
    Returns [remaining_text, telemetry]
    """
    parsed = {}
    match = re.findall(r"^(.*?)\|([!-{]{4,14})\|(.*)$", text)

    if match and len(match[0][1]) % 2 == 0:
        text, telemetry, post = match[0]
        text += post

        temp = [0] * 7
        for i in range(7):
            temp[i] = to_decimal(telemetry[i*2:i*2+2])

        parsed.update({
            u'telemetry': {
                u'seq': temp[0],
                u'vals': temp[1:6]
                }
            })

        if temp[6] != '':
            parsed[u'telemetry'].update({
                u'bits': u"{0:08b}".format(temp[6] & 0xFF)[::-1]
                })

    return text, parsed

def parse_dao(body, parsed):
    match = re.findall("^(.*)\!([\x21-\x7b])([\x20-\x7b]{2})\!(.*?)$", body)
    if match:
        body, daobyte, dao, rest = match[0]
        body += rest

        parsed.update({u'daodatumbyte': daobyte.upper()})
        lat_offset = lon_offset = 0

        if daobyte == u'W' and dao.isdigit():
            lat_offset = int(dao[0]) * 0.001 / 60
            lon_offset = int(dao[1]) * 0.001 / 60
        elif daobyte == u'w' and ' ' not in dao:
            lat_offset = (to_decimal(dao[0]) / 91.0) * 0.01 / 60
            lon_offset = (to_decimal(dao[1]) / 91.0) * 0.01 / 60

        parsed[u'latitude'] += lat_offset if parsed[u'latitude'] >= 0 else -lat_offset
        parsed[u'longitude'] += lon_offset if parsed[u'longitude'] >= 0 else -lon_offset

    return body

def parse_mice(body, dstcall=u"APRS64"):
    u"""
    :param body:
    :param dstcall:
    :return:

    Mic-encoded packet
    'lllc/s$/.........         Mic-E no message capability
    'lllc/s$/>........         Mic-E message capability
    `lllc/s$/>........         Mic-E old posit
    """
    parsed = {u'format': u'mic-e'}

    dstcall = dstcall.split(u'-')[0]

    # verify mic-e format
    if len(dstcall) != 6:
        raise Exception(u"dstcall has to be 6 characters")

    if len(body) < 8:
        raise Exception(u"packet data field is too short")

    if not re.match(r"^[0-9A-Z]{3}[0-9L-Z]{3}$", dstcall):
        raise Exception(u"invalid dstcall")

    if False and not re.match(r"^[&-\x7f][&-a][\x1c-\x7f]{2}[\x1c-\x7d]"
                              r"[\x1c-\x7f][\x21-\x7e][\/\\0-9A-Z]", body):
        raise Exception("invalid data format")

    # get symbol table and symbol
    parsed.update({u'symbol': body[6], u'symbol_table': body[7]})

    # parse latitude
    # the routine translates each characters into a lat digit as described in
    # 'Mic-E Destination Address Field Encoding' table
    tmpdstcall = u""
    for i in dstcall:
        if i in u"KLZ":  # spaces
            tmpdstcall += " "
        elif ord(i) > 76:  # P-Y
            tmpdstcall += chr(ord(i) - 32)
        elif ord(i) > 57:  # A-J
            tmpdstcall += chr(ord(i) - 17)
        else:  # 0-9
            tmpdstcall += i

    # determine position ambiguity
    match = re.findall(r"^\d+( *)$", tmpdstcall)
    if not match:
        raise Exception(u"Invalid latitude ambiguity")

    posambiguity = len(match[0])
    parsed.update({u'posambiguity': posambiguity})

    # adjust the coordinates be in center of ambiguity box
    tmpdstcall = list(tmpdstcall)
    if posambiguity > 0:
        if posambiguity >= 4:
            tmpdstcall[2] = u'3'
        else:
            tmpdstcall[6 - posambiguity] = u'5'

    tmpdstcall = "".join(tmpdstcall)

    latminutes = float((u"%s.%s" % (tmpdstcall[2:4], tmpdstcall[4:6])).replace(u" ", u"0"))
    latitude = int(tmpdstcall[0:2]) + (latminutes / 60.0)

    # determine the sign N/S
    latitude = -latitude if ord(dstcall[3]) <= 0x4c else latitude

    parsed.update({u'latitude': latitude})

    # parse message bits

    mbits = re.sub(r"[0-9L]", "0", dstcall[0:3])
    mbits = re.sub(r"[P-Z]", "1", mbits)
    mbits = re.sub(r"[A-K]", "2", mbits)

    parsed.update({u'mbits': mbits})

    # resolve message type

    if mbits.find(u"2") > -1:
        parsed.update({u'mtype': MTYPE_TABLE_CUSTOM[mbits.replace("2", "1")]})
    else:
        parsed.update({u'mtype': MTYPE_TABLE_STD[mbits]})

    # parse longitude
    longitude = ord(body[0]) - 28  # decimal part of longitude
    longitude += 100 if ord(dstcall[4]) >= 0x50 else 0  # apply lng offset
    longitude += -80 if longitude >= 180 and longitude <= 189 else 0
    longitude += -190 if longitude >= 190 and longitude <= 199 else 0

    # long minutes
    lngminutes = ord(body[1]) - 28.0
    lngminutes += -60 if lngminutes >= 60 else 0

    # + (long hundredths of minutes)
    lngminutes += ((ord(body[2]) - 28.0) / 100.0)

    # apply position ambiguity
    # routines adjust longitude to center of the ambiguity box
    if posambiguity is 4:
        lngminutes = 30
    elif posambiguity is 3:
        lngminutes = (math.floor(lngminutes / 10) + 0.5) * 10
    elif posambiguity is 2:
        lngminutes = math.floor(lngminutes) + 0.5
    elif posambiguity is 1:
        lngminutes = (math.floor(lngminutes * 10) + 0.5) / 10.0
    elif posambiguity is not 0:
        raise Exception(u"Unsupported position ambiguity: %d" % posambiguity)

    longitude += lngminutes / 60.0

    # apply E/W sign
    longitude = 0 - longitude if ord(dstcall[5]) >= 0x50 else longitude

    parsed.update({u'longitude': longitude})

    # parse speed and course
    speed = (ord(body[3]) - 28) * 10
    course = ord(body[4]) - 28
    quotient = int(course / 10.0)
    course += -(quotient * 10)
    course = course * 100 + ord(body[5]) - 28
    speed += quotient

    speed += -800 if speed >= 800 else 0
    course += -400 if course >= 400 else 0

    speed *= 1.852  # knots * 1.852 = kmph
    parsed.update({u'speed': speed, u'course': course})

    # the rest of the packet can contain telemetry and comment
    if len(body) > 8:
        body = body[8:]

        # check for optional 2 or 5 channel telemetry
        match = re.findall(r"^('[0-9a-f]{10}|`[0-9a-f]{4})(.*)$", body)
        if match:
            hexdata, body = match[0]

            hexdata = hexdata[1:]  # remove telemtry flag
            channels = len(hexdata) / 2  # determine number of channels
            hexdata = int(hexdata, 16)  # convert hex to int

            telemetry = []
            for i in range(channels):
                telemetry.insert(0, int(hexdata >> 8 * i & 255))

            parsed.update({u'telemetry': telemetry})

        # check for optional altitude
        match = re.findall(r"^(.*)([!-{]{3})\}(.*)$", body)
        if match:
            body, altitude, extra = match[0]

            altitude = to_decimal(altitude) - 10000
            parsed.update({u'altitude': altitude})

            body = body + extra

        # attempt to parse comment telemetry
        try:
            body, telemetry = parse_comment_telemetry(body)
            parsed.update(telemetry)

        except Exception:
            pass

        # parse DAO extention
        body = parse_dao(body, parsed)

        # rest is a comment
        parsed.update({u'comment': body.strip(' ')})

    return parsed

if __name__ == u"__main__":
    test_message = u"M0XER-4>APRS64,TF3RPF,WIDE2*,qAR,TF3SUT-2:`m0xmJ_k/`\"47}Just truckin'_%"
    test_body = u"`m0xmJ_k/`\"47}Just truckin'_%"

    m = parse_mice(test_body)

    if m:
        logger.info(u"+++ Looks good! +++")
        for k, v in m[1].items():
            logger.info("%s = %s" % (k, v))
