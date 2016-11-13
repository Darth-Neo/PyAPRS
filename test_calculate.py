#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = u"james.morris"
from geo_lib import *

from Logger import *

logger = setupLogging(__name__)
logger.setLevel(DEBUG)


def test_calculate():
    # Test
    city1 = xyz(52.518611, 13.408056)
    city2 = xyz(48.137222, 11.575556)
    gl = calculate(city1, city2, display=True)

    logger.info(u"%s" % gl[0])
    logger.info(u"%s" % gl[1])
    logger.info(u"%s" % gl[2])

    return gl


def test_calculateFromHome(lat, lon, display=True):
    reading_lat = None
    reading_lon = None

    # Latitude:  28.25.065 N =>  28.4347222
    # Longitude: 81.41.868 W => -81.9244444
    home_lat = degree_to_decimal(28, 25, 65)
    home_lon = degree_to_decimal(81, 41, 868)

    if isinstance(lat, (str, unicode)):

        # Latitude :  2831.07N
        # Longitude:  08142.92W
        lat_d = int(lat[0:2])
        lat_m = int(lat[2:4])
        lat_s = int(lat[5:7])

        lon_d = int(lon[1:3])
        lon_m = int(lon[3:5])
        lon_s = int(lon[6:8])

        reading_lat = degree_to_decimal(lat_d, lat_m, lat_s)
        reading_lon = degree_to_decimal(lon_d, lon_m, lon_s)

    elif isinstance(lat, float):
        reading_lat = lat
        reading_lon = lon

    else:
        return None

    home = xyz(home_lat, home_lon)
    city = xyz(reading_lat, reading_lon)

    gl = calculate(home, city, display=True)

    logger.debug(u"_____________________________________________________")
    logger.debug(u"%3.2f Miles" % gl[0][0])
    logger.debug(u"%3.2f Magnetic North" % gl[2][0])
    logger.debug(u"%3.2f True North" % gl[2][1])
    logger.debug(u"%3.2f %s Declination" % (gl[1][0], gl[1][1]))

    logger.debug(u"%3.2f \ %3.2f" % (gl[0][0], gl[2][1]))

    return gl


if __name__ == u"__main__":
    test_calculate()

    lat = 28.818
    lon = abs(-82.256)
    test_calculateFromHome(lat, lon, display=True)

    lat = u"2831.07N"
    lon = u"08142.92W"
    test_calculateFromHome(lat, lon, display=True)
