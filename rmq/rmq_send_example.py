#!/usr/bin/env python
import pika
import time
import random
from ConfigParser import *

from Logger import *
logger = setupLogging(__name__)
logger.setLevel(INFO)

if __name__ == u"__main__":

    configFile = u"rmq_settings.conf"
    Config = ConfigParser()
    Config.read(configFile)

    vhost = ConfigSectionMap(u"Send", Config)[u'vhost']
    queue = ConfigSectionMap(u"Send", Config)[u'queue']
    routing_key = ConfigSectionMap(u"Send", Config)[u'routing_key']
    exchange = ConfigSectionMap(u"Send", Config)[u'exchange']

    host = ConfigSectionMap(u"Send", Config)[u'host']
    port = int(ConfigSectionMap(u"Send", Config)[u'port'])

    username = ConfigSectionMap(u"Send", Config)[u'username']
    password = ConfigSectionMap(u"Send", Config)[u'password']

    logger.info(u"Host : %s" % host)

    credentials = pika.PlainCredentials(username, password)

    n = 0
    m = 100

    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=host, port=port, virtual_host=vhost, credentials=credentials))

        channel = connection.channel()

        for n in range(1,m):
            try:
                body = u"%20s %20s %20s %5d" % (exchange, routing_key, queue, n)
                channel.basic_publish(exchange=exchange, routing_key=routing_key, body=body)
                logger.info(u"%3d %s" % (n, body))

            except Exception, msg:
                logger.error(u"%s" % msg)

            d = random.randint(1, 5)
            logger.info(u"Sleep : %d" % d)
            time.sleep(d)

        connection.close()

    except KeyboardInterrupt:
        logger.info(u"Bye!")

    except Exception, msg:
        logger.info(u"Ops... : %s" % msg)
