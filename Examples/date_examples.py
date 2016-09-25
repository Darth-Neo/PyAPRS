# !/usr/bin/python
import datetime

i = datetime.datetime.now()

print ("Current date & time = %s" % i)

print ("Date and time in ISO format = %s" % i.isoformat())

print ("Current year = %s" % i.year)

print ("Current month = %s" % i.month)

print ("Current date (day) =  %s" % i.day)

print ("dd/mm/yyyy format =  %s/%s/%s" % (i.day, i.month, i.year))

print ("Current hour = %s" % i.hour)

print ("Current minute = %s" % i.minute)

print ("Current second =  %s" % i.second)

print ("hh:mm:ss format = %s:%s:%s" % (i.hour, i.month, i.second))