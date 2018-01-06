#!/usr/bin/env python
import pika
from ConfigParser import *

from Logger import *
logger = setupLogging(__name__)
logger.setLevel(INFO)


class RabbitRecieve(object):
    def __init__(self, configFile=None):

        if configFile is None: configFile = u"rmq_settings.conf"
        Config = ConfigParser()
        Config.read(configFile)

        self.vhost = ConfigSectionMap(u"Receive", Config)[u'vhost']
        self.queue = ConfigSectionMap(u"Receive", Config)[u'queue']
        self.routing_key = ConfigSectionMap(u"Receive", Config)[u'routing_key']
        self.exchange = ConfigSectionMap(u"Receive", Config)[u'exchange']

        self.host = ConfigSectionMap(u"Receive", Config)[u'host']
        self.port = int(ConfigSectionMap(u"Receive", Config)[u'port'])

        username = ConfigSectionMap(u"Receive", Config)[u'username']
        password = ConfigSectionMap(u"Receive", Config)[u'password']
        self.credentials = pika.PlainCredentials(username, password)

        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=self.host, port=self.port, virtual_host=self.vhost, credentials=self.credentials))

        self.channel = self.connection.channel()

    def __del__(self):
        pass

    def __repr__(self):
        """
        Represent the info about the instance.
        :rtype: str
        """
        value = u"<%s host=%s port=%s virtual_host=%s>" % (self.host, self.port, self.vhost, self.queue)
        return value

    @staticmethod
    def recieve_callback(ch, method, properties, body):
        logger.debug(u"ch : {0}".format(ch))
        logger.debug(u"method : {0}".format(method))
        logger.debug(u"properties : {0}".format(properties))
        logger.info(u"Received %r" % body)

    def recieve_messages(self, f=None):
        if f is None:
            f = RabbitRecieve.recieve_callback

        self.channel.basic_consume(f, queue=self.queue, no_ack=True)

        logger.debug(u" [*] Waiting for messages. To exit press CTRL+C")

        try:
            self.channel.start_consuming()

        except KeyboardInterrupt, msg:
            logger.info(u"Bye")


def test_recieve_message():
    rbr = RabbitRecieve()

    try:
        rbr.recieve_messages()

    except KeyboardInterrupt, msg:
        logger.info(u"Bye")


if __name__ == u"__main__":
    test_recieve_message()
