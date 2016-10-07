#!/usr/bin/env python

import sys
import Adafruit_CharLCD as LCD
from time import sleep, strftime
from rmq.rmq_receive import *
from rmq.rmq_send import *

lcd = LCD.Adafruit_CharLCDPlate()
lcd.clear()
lcd.set_color(0, 1, 0)
lcd.set_backlight(1)
lcd.message(u"Hello James")

lcd_columns = 16

colors = [[0, 0, 0],  #
          [0, 0, 1],  # Blue
          [0, 1, 0],  # Green
          [0, 1, 1],  # Light Blue
          [1, 0, 0],  # Red
          [1, 0, 1],  # Purple
          [1, 1, 0],  # Light Green
          [1, 1, 1]]  # Lighter Blue


def recieve_callback(ch, method, properties, body):
    global lcd

    logger.info(u"Received [%s] : %d" % (body.strip("\n"), len(body)))

    lcd.clear()
    lcd.set_color(0, 1, 0)
    lcd.message(body)

    if False:
        for i in range(lcd_columns - len(body)):
            time.sleep(0.3)
            lcd.move_right()

        for i in range(lcd_columns - len(body)):
            time.sleep(0.3)
            lcd.move_left()

    time.sleep(0.75)


if __name__ == "__main__":
    configFile = u"." + os.sep + u"rmq" + os.sep + u"rmq_settings.conf"
    logger.info(u"%s" % configFile)
    rbr = RabbitRecieve(configFile=configFile)
    rbr.recieve_messages(recieve_callback)

