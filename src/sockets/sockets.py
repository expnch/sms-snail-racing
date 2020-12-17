#!/usr/bin/env python

import asyncio
import asyncio_redis
import json
import logging
import os
import redis
import websockets

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

REDIS_HOST = os.environ.get('REDIS_HOST', '0.0.0.0')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
WEBSOCKETS_PORT = int(os.environ.get('WEBSOCKETS_PORT', 6789))

# Connect to Redis
async def get_subscriber(channel):
    connection = await asyncio_redis.Connection.create(host=REDIS_HOST, port=REDIS_PORT)
    subscriber = await connection.start_subscribe()
    await subscriber.subscribe([channel])
    return connection, subscriber

# Websockets handler
async def handler(websocket, path):
    logging.info("Sockets subscribed new client")
    connection, subscriber = await get_subscriber('messages')
    try:
        while True:
            reply = await subscriber.next_published()
            logging.info("Sockets published a message: {}".format(reply.value))
            await websocket.send(reply.value)
    finally:
        connection.close()
        logging.info("Sockets client left")

# Start async
loop = asyncio.get_event_loop()
start_server = websockets.serve(handler, "0.0.0.0", WEBSOCKETS_PORT)
loop.run_until_complete(start_server)
loop.run_forever()
