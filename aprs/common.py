import re
import time
import base91
from datetime import datetime
from telemetry import parse_comment_telemetry

from Logger import *
logger = setupLogging(__name__)
logger.setLevel(INFO)


__all__ = [
    "validate_callsign",
    "parse_header",
    "parse_timestamp",
    "parse_comment",
    "parse_data_extentions",
    "parse_comment_altitude",
    "parse_dao",
    ]

def validate_callsign(callsign, prefix=""):
    prefix = "%s: " % prefix if bool(prefix) else ""

    match = re.findall(r"^([A-Z0-9]{1,6})(-(\d{1,2}))?$", callsign)

    if not match:
        raise Exception("%sinvalid callsign" % prefix)

    callsign, _, ssid = match[0]

    if bool(ssid) and int(ssid) > 15:
        raise Exception("%sssid not in 0-15 range" % prefix)


def parse_header(head):
    """
    Parses the header part of packet
    Returns a dict
    """
    try:
        (fromcall, path) = head.split(">", 1)
    except:
        raise Exception("invalid packet header")

    if (not 1 <= len(fromcall) <= 9 or
       not re.findall(r"^[a-z0-9]{0,9}(\-[a-z0-9]{1,8})?$", fromcall, re.I)):

        raise Exception("fromcallsign is invalid")

    path = path.split(",")

    if len(path[0]) == 0:
        raise Exception("no tocallsign in header")

    tocall = path[0]
    path = path[1:]

    validate_callsign(tocall, "tocallsign")

    for digi in path:
        if not re.findall(r"^[A-Z0-9\-]{1,9}\*?$", digi, re.I):
            raise Exception("invalid callsign in path")

    parsed = {"from": fromcall,"to": tocall,"path": path,}

    viacall = ""
    if len(path) >= 2 and re.match(r"^q..$", path[-2]):
        viacall = path[-1]

    pd = {"via": viacall}
    parsed.update(pd)
    return parsed


def parse_timestamp(body, packet_type=""):
    parsed = {}

    match = re.findall(r"^((\d{6})(.))$", body[0:7])
    if match:
        rawts, ts, form = match[0]
        utc = datetime.utcnow()

        timestamp = 0

        if packet_type == ">" and form != "z":
            pass
        else:
            body = body[7:]

            try:
                # zulu hhmmss format
                if form == "h":
                    timestamp = "%d%02d%02d%s" % (utc.year, utc.month, utc.day, ts)
                # zulu ddhhmm format
                # "/" local ddhhmm format
                elif form in "z/":
                    timestamp = "%d%02d%s%02d" % (utc.year, utc.month, ts, 0)
                else:
                    timestamp = "19700101000000"

                timestamp = utc.strptime(timestamp, "%Y%m%d%H%M%S")
                timestamp = time.mktime(timestamp.timetuple())

            except Exception as exp:
                timestamp = 0
                logger.debug(exp)

        pd = {"raw_timestamp": rawts,"timestamp": int(timestamp),}
        parsed.update(pd)

    rl = (body, parsed)
    return rl


def parse_comment(body, parsed):
    body, result = parse_data_extentions(body)
    parsed.update(result)

    body, result = parse_comment_altitude(body)
    parsed.update(result)

    body, result = parse_comment_telemetry(body)
    parsed.update(result)

    body = parse_dao(body, parsed)

    if len(body) > 0 and body[0] == "/":
        body = body[1:]

    pd = {"comment": body.strip(" ")}
    parsed.update(pd)


def parse_data_extentions(body):
    parsed = dict()
    match = re.findall(r"^([0-9 .]{3})/([0-9 .]{3})", body)

    if match:
        cse, spd = match[0]
        body = body[7:]
        pd = {"course": int(cse) if cse.isdigit() and 1 <= int(cse) <= 360 else 0}
        parsed.update(pd)

        if spd.isdigit():
            pd = {"speed": int(spd)*1.852}
            parsed.update(pd)

        match = re.findall(r"^/([0-9 .]{3})/([0-9 .]{3})", body)
        if match:
            brg, nrq = match[0]
            body = body[8:]
            if brg.isdigit():
                pd = {"bearing": int(brg)}
                parsed.update(pd)
            if nrq.isdigit():
                pd = {"nrq": int(nrq)}
                parsed.update(pd)
    else:
        match = re.findall(r"^(PHG(\d[\x30-\x7e]\d\d[0-9A-Z]?))", body)
        if match:
            ext, phg = match[0]
            body = body[len(ext):]
            pd = {"phg": phg}
            parsed.update(pd)
        else:
            match = re.findall(r"^RNG(\d{4})", body)
            if match:
                rng = match[0]
                body = body[7:]
                pd = {"rng": int(rng) * 1.609344}  # miles to km
                parsed.update(pd)

    return body, parsed


def parse_comment_altitude(body):
    parsed = {}
    match = re.findall(r"^(.*?)/A=(\-\d{5}|\d{6})(.*)$", body)
    if match:
        body, altitude, rest = match[0]
        body += rest
        pd = {"altitude": int(altitude)*0.3048}
        parsed.update(pd)

    return body, parsed


def parse_dao(body, parsed):
    match = re.findall("^(.*)\!([\x21-\x7b])([\x20-\x7b]{2})\!(.*?)$", body)
    if match:
        body, daobyte, dao, rest = match[0]
        body += rest

        pd =  {"daodatumbyte": daobyte.upper()}
        parsed.update(pd)
        lat_offset = lon_offset = 0

        if daobyte == "W" and dao.isdigit():
            lat_offset = int(dao[0]) * 0.001 / 60
            lon_offset = int(dao[1]) * 0.001 / 60

        elif daobyte == "w" and " " not in dao:
            lat_offset = (base91.to_decimal(dao[0]) / 91.0) * 0.01 / 60
            lon_offset = (base91.to_decimal(dao[1]) / 91.0) * 0.01 / 60

        parsed["latitude"] += lat_offset if parsed["latitude"] >= 0 else -lat_offset
        parsed["longitude"] += lon_offset if parsed["longitude"] >= 0 else -lon_offset

    return body
