#!/usr/bin/env python
import pika
import time
import random


if __name__ == "__main__":

    vhost = "aprs"
    queue = "aprs_queue"
    routing_key = "temp_bp_hum"
    exchange = "simple"
    host = "192.168.1.125"
    port = 5672

    username = "weather"
    password = "w1nner"

    credentials = pika.PlainCredentials(username, password)

    n = 0
    m = 100

    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=host, port=port, virtual_host=vhost, credentials=credentials))

        channel = connection.channel()
        # channel.queue_declare(queue=queue)

        for n in range(1,m):
            try:
                body = "%s \t%s \t %s : %d" % (exchange, routing_key, queue, n)
                channel.basic_publish(exchange=exchange, routing_key=routing_key, body=body)
                print(" [%d] %s" % (n, body))

            except Exception, msg:
                print("%s" % msg)

            d = random.randint(1, 5)
            print("Sleep : %d" % d)
            time.sleep(d)

        connection.close()

    except KeyboardInterrupt:
        print "Bye!"

    except Exception, msg:
        print "Ops... : %s" % msg




