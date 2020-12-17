#!/usr/bin/env python

from flask import Flask, request
import json
import logging
import os
import redis
import requests

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

ZW_SESSION_KEY = os.environ.get("ZW_SESSION_KEY")

NGROK_AUTH_TOKEN = os.environ.get("NGROK_AUTH_TOKEN")

REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))

WEB_PORT = int(os.environ.get("WEB_PORT", "5000"))

def register_webhook(base_url, path="/", headers={"Content-Type": "application/x-www-form-urlencoded"}):
    print("Registering webhook on {}".format(base_url+path))
    payload = {'session': ZW_SESSION_KEY
              ,'type': 'message'
              ,'event': 'receive'
              ,'url': base_url + path
              }
    r = requests.post("https://api.zipwhip.com/webhook/add", data=payload, headers=headers)
    if r.status_code != 200:
        print("Hook registration failed with response {}\n{}".format(r.status_code, r.text))

app = Flask(__name__)

# Start Ngrok
from pyngrok import ngrok
ngrok.set_auth_token(NGROK_AUTH_TOKEN)
public_url = ngrok.connect(WEB_PORT).public_url
logging.info("Ngrok tunneling {} -> http://127.0.0.1:{}".format(public_url, WEB_PORT))

# Connect to Redis
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)

# Register webhook
register_webhook(public_url)

# Define routes
@app.route('/', methods=['GET'])
def hello():
    return "Hello, world"

@app.route('/', methods=['POST'])
@app.route('/message/receive', methods=['POST'])
def message_receive():
    body = json.loads(request.get_data())['body']
    logging.info("Hooks received message: {}".format(body))
    payload = {'type': 'cheer', 'body': body}
    r.publish("messages", json.dumps(payload))
    return "Message received"
