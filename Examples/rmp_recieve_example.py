#!/usr/bin/env python
import pika


if __name__ == u"__main__":

    vhost = "aprs"
    queue = "aprs_queue"
    routing_key = "temp_bp_hum"
    exchange = "simple"
    host = "localhost"
    port = 5672

    username = "weather"
    password = "w1nner"

    credentials = pika.PlainCredentials(username, password)

    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=host, port=port, virtual_host=vhost, credentials=credentials))

    channel = connection.channel()

    # channel.queue_declare(queue=queue)

    def callback(ch, method, properties, body):
        print(" [x] Received %r" % body)


    channel.basic_consume(callback, queue=queue, no_ack=True)

    print(" [*] Waiting for messages. To exit press CTRL+C")

    try:
        channel.start_consuming()

    except KeyboardInterrupt, msg:
        print("Bye")