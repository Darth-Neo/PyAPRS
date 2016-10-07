# aprslib - Python library for working with APRS

"""
This module contains all function used in parsing packets
"""
import re
import chardet
from common import *
from misc import *
from position import *
from mice import *
from message import *
from telemetry import *
from weather import *

from Logger import *
logger = setupLogging(__name__)
logger.setLevel(INFO)


def parse(packet):

    if len(packet) == 0:
        raise Exception("packet is empty", packet)

    packet = packet.rstrip("\r\n")
    logger.debug("Parsing: %s", packet)

    # split into head and body
    try:
        (head, body) = packet.split(":", 1)
    except:
        raise Exception("packet has no body", packet)

    if len(body) == 0:
        raise Exception("packet body is empty", packet)

    parsed = {"raw": packet,}

    # parse head
    try:
        pd = parse_header(head)
        parsed.update(pd)
    except Exception, msg:
        raise Exception(str(msg), packet)

    # parse body
    packet_type = body[0]
    body = body[1:]

    if len(body) == 0 and packet_type != ">":
        raise Exception("packet body is empty after packet type character", packet)

    parse_body(packet_type, body, parsed)

    # if we fail all attempts to parse, try beacon packet
    if "format" not in parsed:
        if not re.match(r"^(AIR.*|ALL.*|AP.*|BEACON|CQ.*|GPS.*|DF.*|DGPS.*|"
                        "DRILL.*|DX.*|ID.*|JAVA.*|MAIL.*|MICE.*|QST.*|QTH.*|"
                        "RTCM.*|SKY.*|SPACE.*|SPC.*|SYM.*|TEL.*|TEST.*|TLM.*|"
                        "WX.*|ZIP.*|UIDIGI)$", parsed["to"]):
            raise Exception("format is not supported", packet)

        parsed.update({"format": "beacon", "text": packet_type + body,})

    logger.debug("Parsed ok.")
    return parsed


def parse_body(packet_type, body, parsed):
    result = {}

    # NOT SUPPORTED FORMATS
    #
    # # - raw weather report
    # $ - raw gps
    # % - agrelo
    # & - reserved
    # ( - unused
    # ) - item report
    # * - complete weather report
    # + - reserved
    # - - unused
    # . - reserved
    # < - station capabilities
    # ? - general query format
    # T - telemetry report
    # [ - maidenhead locator beacon
    # \ - unused
    # ] - unused
    # ^ - unused
    # } - 3rd party traffic
    if packet_type in "#$%)*<?T[}":
        raise Exception("format is not supported")

    # user defined
    elif packet_type in ",":
        logger.debug("Packet is invalid format")

        body, result = parse_invalid(body)

    # user defined
    elif packet_type in "{":
        logger.debug("Packet is user-defined")

        body, result = parse_user_defined(body)

    # Status report
    elif packet_type in ">":
        logger.debug("Packet is just a status message")

        body, result = parse_status(packet_type, body)

    # Mic-encoded packet
    elif packet_type in "`":
        logger.debug("Attempting to parse as mic-e packet")

        body, result = parse_mice(parsed["to"], body)

    # Message packet
    elif packet_type in ":":
        logger.debug("Attempting to parse as message packet")

        body, result = parse_message(body)

    # Positionless weather report
    elif packet_type in "_":
        logger.debug("Attempting to parse as positionless weather report")

        body, result = parse_weather(body)

    # postion report (regular or compressed)
    elif (packet_type in "!=/@;" or
          0 <= body.find("!") < 40):  # page 28 of spec (PDF)

        body, result = parse_position(packet_type, body)

        if len(body) != 0 and packet_type in "/@":
            body, result = parse_weather(body)

    # we are done
    parsed.update(result)

