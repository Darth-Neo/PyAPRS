#!/usr/bin/env python
from datetime import datetime, timedelta

intervals = (
    ('weeks', 604800),  # 60 * 60 * 24 * 7
    ('days', 86400),  # 60 * 60 * 24
    ('hours', 3600),  # 60 * 60
    ('minutes', 60),
    ('seconds', 1),
)

def getTime():
    sec = timedelta(seconds=int(input('Enter the number of minutes: ')))
    d = datetime(1,1,1) + sec

    print("DAYS:HOURS:MIN:SEC")
    print("%d:%d:%d:%d" % (d.day-1, d.hour, d.minute, d.second))


def display_time(seconds, granularity=2):
    result = []

    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append("{} {}".format(value, name))

    return ', '.join(result[:granularity])

if __name__ == u"__main__":

    if False:
        getTime()
    else:
        value = 1200 * 60
        print display_time(value)


