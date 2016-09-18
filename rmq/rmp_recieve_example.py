#!/usr/bin/env python
import pika
from ConfigParser import *

from Logger import *
logger = setupLogging(__name__)
logger.setLevel(INFO)

if __name__ == u"__main__":
    configFile = u"rmq_settings.conf"
    Config = ConfigParser()
    Config.read(configFile)

    vhost = ConfigSectionMap(u"Receive", Config)[u'vhost']
    queue = ConfigSectionMap(u"Receive", Config)[u'queue']
    routing_key = ConfigSectionMap(u"Receive", Config)[u'routing_key']
    exchange = ConfigSectionMap(u"Receive", Config)[u'exchange']
    host = ConfigSectionMap(u"Receive", Config)[u'host']
    port = int(ConfigSectionMap(u"Receive", Config)[u'port'])
    username = ConfigSectionMap(u"Receive", Config)[u'username']
    password = ConfigSectionMap(u"Receive", Config)[u'password']

    logger.info(u"Host : %s" % host)

    credentials = pika.PlainCredentials(username, password)

    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=host, port=port, virtual_host=vhost, credentials=credentials))

    channel = connection.channel()

    def callback(ch, method, properties, body):
        logger.info(u"Received %r" % body)


    channel.basic_consume(callback, queue=queue, no_ack=True)

    logger.info(u" [*] Waiting for messages. To exit press CTRL+C")

    try:
        channel.start_consuming()

    except KeyboardInterrupt, msg:
        logger.info(u"Bye")