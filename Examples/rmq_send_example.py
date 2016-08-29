#!/usr/bin/env python
import pika

if __name__ == u"__main__":

    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters("192.168.1.125"))
        channel = connection.channel()

        channel.queue_declare(queue="hello")

        channel.basic_publish(exchange="", routing_key="hello", body="Hello World!")

        print(" [x] Sent 'Hello World!'")

        connection.close()

    except Exception, msg:
        print("%s" % msg)


