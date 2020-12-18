#!/usr/bin/env python

from game import Game
import json
import logging
import os
import re
import redis
import time

REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

# Handlers
def message_handler(m):
    text = m['data'].decode('UTF-8').upper()
    for snail_id, pattern in re_patterns:
        if pattern.match(text):
            if g.state in ['ready', 'race']:
                cheer(snail_id, text)
            break

def command_handler(m):
    text = m['data'].decode('UTF-8').upper()
    if text == "NEXT":
        g.change_state()

def cheer(snail_id, text):
    g.change_velocity(snail_id, amount=1)

# Connect to Redis
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
p = r.pubsub(ignore_subscribe_messages=True)
p.subscribe(**{'messages': message_handler, 'commands': command_handler})

# Game state
g = Game(r, goal=100, jitter=2)
re_patterns = [(k, re.compile('.*' + g.names[k].upper())) for k in g.names]

# Main loop
thread = p.run_in_thread(sleep_time=0.001)
while True:
    if g.state in ['setup']:
        logging.info('[setup] Waiting for status command...')
    elif g.state in ['ready']:
        logging.info('[ready] Starting race in {}s'.format(g.countdown))
    elif g.state == 'race':
        logging.info('[race] {} ({}) to {} ({}) to {} ({})'.format(g.position['0'], g.velocity['0'], g.position['1'], g.velocity['1'], g.position['2'], g.velocity['2']))
    elif g.state == 'victory':
        logging.info('[victory] {} won; waiting for status command...'.format(g.winners, g.countdown))
    g.process()
    time.sleep(1)

thread.stop()
