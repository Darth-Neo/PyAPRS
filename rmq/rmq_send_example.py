#!/usr/bin/env python
import pika
import time
import random
from ConfigParser import *

from Logger import *

logger = setupLogging(__name__)
logger.setLevel(INFO)


class RabbitSend(object):
    """
    Class for sending RabbitMQ Messages
    """

    def __init__(self, configFile=None):
        """
        Initialize all values and setup
        :param configFile:
        """

        if configFile is None: configFile = u"rmq_settings.conf"

        Config = ConfigParser()
        Config.read(configFile)

        self.vhost = ConfigSectionMap(u"Send", Config)[u'vhost']
        self.queue = ConfigSectionMap(u"Send", Config)[u'queue']
        self.routing_key = ConfigSectionMap(u"Send", Config)[u'routing_key']
        self.exchange = ConfigSectionMap(u"Send", Config)[u'exchange']

        self.host = ConfigSectionMap(u"Send", Config)[u'host']
        self.port = int(ConfigSectionMap(u"Send", Config)[u'port'])

        username = ConfigSectionMap(u"Send", Config)[u'username']
        password = ConfigSectionMap(u"Send", Config)[u'password']
        credentials = pika.PlainCredentials(username, password)

        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=self.host, port=self.port, virtual_host=self.vhost, credentials=credentials))

        self.channel = self.connection.channel()

    def __del__(self):
        """
        Close connection when finished
        :return:
        """
        self.connection.close()

    def __repr__(self):
        """
        Represent the info about the instance.
        :rtype: str
        """
        return (u"<%s host=%s port=%s virtual_host=%s>" % (self.__class__.__name__, self.host, self.port, self.vhost))

    def send_message(self, message):
        """
        Send Message to host system
        :param message:
        :return:
        """
        try:
            self.channel.basic_publish(exchange=self.exchange, routing_key=self.routing_key, body=message)

        except KeyboardInterrupt:
            logger.info(u"Bye!")

        except Exception, msg:
            logger.info(u"Ops, ... : %s" % msg)


def test_send_message(m=100, max=5):
    rbs = RabbitSend()

    try:
        for n in range(1, m):
            body = u"%20s %20s %20s %5d" % (rbs.exchange, rbs.routing_key, rbs.queue, n)
            logger.info(u"%3d %s" % (n, body))
            rbs.send_message(body)

            d = random.randint(1, max)
            time.sleep(d)

    except KeyboardInterrupt:
        logger.info(u"Bye!")

    except Exception, msg:
        logger.info(u"Ops... : %s" % msg)


if __name__ == u"__main__":
    test_send_message()
