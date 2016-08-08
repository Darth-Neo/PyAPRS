#!/usr/bin/env python
import pika

if __name__ == u"__main__":
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
    channel = connection.channel()

    channel.queue_declare(queue="hello")

    def callback(ch, method, properties, body):
        print(" [x] Received %r" % body)

    channel.basic_consume(callback, queue="hello", no_ack=True)

    print(" [*] Waiting for messages. To exit press CTRL+C")

    try:
        channel.start_consuming()

    except KeyboardInterrupt, msg:
        print("Bye")