#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = u"james.morris"
import os
from parsing import *

from Logger import *
logger = setupLogging(__name__)
logger.setLevel(INFO)

error_count = 0

def parse_aprs_header(header, footer, n=0):
    global error_count
    header_fields = None
    aprs_addresses = None

    try:
        # fm WC4PEM-10 to APMI06-0 via WC4PEM-14,WIDE2-1 UI  pid=F0
        addresses = header.split(u" ")
        fm = addresses[2]
        to = addresses[4]
        path = addresses[6]

        if path is None or not(len(path) > 1):
            via = addresses[5]
            error_count += 1
            logger.error(u"via is {0!r}".format(via))

        # M0XER-4>APRS64,TF3RPF,WIDE2*,qAR,TF3SUT-2
        aprs_addresses = "{0}>{1},{2}:{3}" .format(fm, to, path, footer)
        message = "{0!r} ->{1!r}-> {2!r}".format(fm, path, to)
        logger.debug(message)

        logger.info(u"%3d [%s]" % (n, header[10:]))
        logger.info(u"    [%s]" % footer)

        header_fields = {"From" : fm, "To" : to, "Path": path}

    except Exception, msg:
        error_count += 1
        logger.error(u"%d[%d] : %s" % (n, error_count, msg))

    return header_fields, aprs_addresses

def showFields(header, footer, n):
    global error_count
    try:
        header_fields, aprs_addresses = parse_aprs_header(header, footer, n)

        fields = parse(aprs_addresses)

        logger.info(u"%d __________________________________________" % n)
        for k, v in fields.items():
            if isinstance(v, dict):
                for k1, v1 in v.items():
                    logger.info(u"    {} : {}".format(k1, v1))

            logger.info(u"{} : {}".format(k, v))

    except Exception, msg:
        error_count += 1
        logger.error(u"%d[%d] : %s" % (n, error_count, msg))

def test_aprs():

    n = 0

    # Not supported
    # header = "AFSK1200: fm KJ4SFE-0 to R7UY6Q-0 via K4LKL-10,WIDE1-0,WC4PEM-14,WIDE2-0 UIv pid=F0"
    # footer = "$ULTW0079006D02EE22D627A8FFF688CF000103E800D900190000005A."
    # logger.debug(u"______________________ Set : 0")
    # showFields(header, footer)

    # 0  : mic-e tests
    header = "AFSK1200: fm KJ4SFE-0 to R7UY6Q-0 via K4LKL-10,WIDE1-0,WC4PEM-14,WIDE2-0 UIv pid=F0"
    footer = "`mUul .-/`4K}Brian - Lakeland ... Ridin' the storm out_"
    logger.debug(u"______________________ Set : %d" % n)
    showFields(header, footer, n)
    n+= 1

    # 1
    header = "AFSK1200: fm KJ4SFE-0 to R7UY6Q-0 via K4LKL-10,WIDE1-0,WC4PEM-14,WIDE2-0 UIv pid=F0"
    footer = "`mSzlIEv\]\"4=}MOBILE="
    logger.debug(u"______________________ Set : %d" % n)
    showFields(header, footer, n)
    n += 1

    # 2
    header = "AFSK1200: fm KJ4SFE-0 to R7UY6Q-0 via K4LKL-10,WIDE1-0,WC4PEM-14,WIDE2-0 UIv pid=F0"
    footer = "`n<fr 4>/`\"4.}443.050MHz T103 +500 Press QSY to talk._"
    logger.debug(u"______________________ Set : %d" % n)
    showFields(header, footer, n)
    n+= 1

    # 3
    header = "AFSK1200: fm K4PKT-1 to APNP50-0 via WC4PEM-15,WC4PEM-14,WIDE2-0 UIv pid=F0"
    footer = "!2643.77NP08054.82W#PHG6530/11,22,21,33 Clewiston, Fl. On the Web pbpg.org"
    logger.debug(u"______________________ Set : %d" % n)
    showFields(header, footer, n)
    n += 1

    # 4
    header = "AFSK1200: fm K4PKT-1 to APNP50-0 via WC4PEM-15,WC4PEM-14,WIDE2-0 UIv pid=F0"
    footer = "_10011556c275s002g005t090r000p001P000h00b10151wDAV"
    logger.debug(u"______________________ Set : %d" % n)
    showFields(header, footer, n)
    n += 1

    # 5
    header = "AFSK1200: fm K4PKT-1 to APNP50-0 via WC4PEM-15,WC4PEM-14,WIDE2-0 UIv pid=F0"
    footer = "=2748.08N/08218.51W-PHG70302/Monitor 443.725/+PL 77 {UIV32N}"
    logger.debug(u"______________________ Set : %d" % n)
    showFields(header, footer, n)
    n += 1

    # 6
    header = "AFSK1200: fm K4PKT-1 to APNP50-0 via WC4PEM-15,WC4PEM-14,WIDE2-0 UIv pid=F0"
    footer = ";145.650  *051916z2749.31N/08244.16Wr/A=000025AA/Cert-Node 273835"
    logger.debug(u"______________________ Set : %d" % n)
    showFields(header, footer, n)
    n += 1

    # 7
    header = "AFSK1200: fm K4PKT-1 to APNP50-0 via WC4PEM-15,WC4PEM-14,WIDE2-0 UIv pid=F0"
    footer = "/042023z2757.15N/08147.20W_125/005g007t079r000p003P004h92b10173"
    logger.debug(u"______________________ Set : %d" % n)
    showFields(header, footer,n )

    # Errors ?
    logger.info(u"__________________________________________")
    logger.info("Passed = %d \t Error Count : %d" % (n, error_count))
    assert error_count == 0

if __name__ == u"__main__":

    test_aprs()