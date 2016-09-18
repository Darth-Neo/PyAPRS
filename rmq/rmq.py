#!/usr/bin/env python
import pika
from ConfigParser import *

from Logger import *
logger = setupLogging(__name__)
logger.setLevel(INFO)

class RMQ(object):
    """
    Encapsulate RabbitMQ functionality for use in APRS Display
    """

    def __init__(self, configFile=None):

        if configFile is None:
            configFile = u"rmq_settings.conf"

        Config = ConfigParser()
        Config.read(configFile)

        self.vhost = ConfigSectionMap(u"Send", Config)[u'vhost']
        self.queue = ConfigSectionMap(u"Send", Config)[u'queue']
        self.routing_key = ConfigSectionMap(u"Send", Config)[u'routing_key']
        self.exchange = ConfigSectionMap(u"Send", Config)[u'exchange']
        self.host = ConfigSectionMap(u"Send", Config)[u'host']
        self.port = int(ConfigSectionMap(u"Send", Config)[u'port'])
        self.username = ConfigSectionMap(u"Send", Config)[u'username']
        self.password = ConfigSectionMap(u"Send", Config)[u'password']

        logger.debug(u"Host : %s" % self.host)

        self.credentials = pika.PlainCredentials(self.username, self.password)

    def send_message(self, message):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(
                host=self.host, port=self.port, virtual_host=self.vhost, credentials=self.credentials))

            channel = connection.channel()

            channel.basic_publish(exchange=self.exchange, routing_key=self.routing_key, body=message)

            logger.debug(u"Message Sent")

        except KeyboardInterrupt:
            logger.info(u"Bye!")

        except Exception, msg:
            logger.info(u"Ops... : %s" % msg)

    @staticmethod
    def _callback(ch, method, properties, body):
        logger.info(u"Received %r" % body)

    def receive_message(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=self.host, port=self.port, virtual_host=self.vhost, credentials=self.credentials))

        channel = connection.channel()

        channel.basic_consume(self._callback, queue=self.queue, no_ack=True)

        logger.info(u" [*] Waiting for messages. To exit press CTRL+C")

        channel.start_consuming()

