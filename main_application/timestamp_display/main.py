import string
import time
import random
import datetime
from flask import Flask, abort
import requests
import os

app = Flask(__name__)

letters = string.ascii_letters
s = ''.join(random.choice(letters) for i in range(25))

@app.route("/health")
def check_availability():
    resp = requests.get('http://pingpong-svc/pingpong/count')

    if (resp.status_code == 200):
        return "OK"
    else:
        abort(500)


@app.route("/")
def get_string():
    timestamp = ''
    with open('/files/timestamp.txt', 'r') as f:
        timestamp = f.read()

    resp = requests.get('http://pingpong-svc/pingpong/count')
    
    message = os.environ['MESSAGE']
    html = f"""<!DOCTYPE HTML>
          <html>
            <head></head>
            <body>
                <p>{message}</p> <br/>
                <p>{timestamp} {s}</p> <br/>
                <p>Ping / Pongs: {resp.text}</p>
            </body>
          </html>"""
    return html

if __name__ == "__main__":
    host = '0.0.0.0'
    port = 5000
    app.run(host=host, port=port)