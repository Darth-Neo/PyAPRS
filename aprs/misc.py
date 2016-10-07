from common import parse_timestamp

from Logger import *
logger = setupLogging(__name__)
logger.setLevel(INFO)

__all__ = [
        "parse_status",
        "parse_invalid",
        "parse_user_defined",
        ]


# STATUS PACKET
#
# >DDHHMMzComments
# >Comments
def parse_status(packet_type, body):
    body, result = parse_timestamp(body, packet_type)
    pd = {"format": "status","status": body.strip(" ")}
    result.update(pd)
    rm = (body, result)
    return rm


# INVALID
#
# ,.........................
def parse_invalid(body):
    rm = ("", {"format": "invalid","body": body})
    return rm


# USER DEFINED
#
# {A1................
# {{.................
def parse_user_defined(body):
    rm = ("", {"format": "user-defined","id": body[0],"type": body[1],"body": body[2:],})
    return rm
