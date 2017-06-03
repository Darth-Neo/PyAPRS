#!/usr/bin/env python

letter_angle = u"YNS"
list_angle = list()
list_angle.append([-1, 11.26, u"N"])
list_angle.append([11.25, 33.75, u"NNE"])
list_angle.append([33.75, 56.25, u"NE"])
list_angle.append([56.25, 78.75, u"ENE"])
list_angle.append([78.75, 101.25, u"E"])
list_angle.append([101.25, 123.75, u"ESE"])
list_angle.append([123.75, 126.26, u"SE"])
list_angle.append([146.25, 168.75, u"SSE"])
list_angle.append([168.75, 191.25, u"S"])
list_angle.append([191.25, 213.75, u"SSW"])
list_angle.append([213.75, 236.25, u"SW"])
list_angle.append([236.25, 258.75, u"WSW"])
list_angle.append([258.75, 281.25, u"W"])
list_angle.append([281.25, 303.75, u"WNW"])
list_angle.append([303.75, 326.25, u"NW"])
list_angle.append([326.25, 348.75, u"NNW"])
list_angle.append([348.75, 360, u"N"])

if __name__ == u"__main__":
    for x in list_angle:
        print("{}".format(x))
