import os
import requests
import sys
from time import time
import json
from flask import Flask
app = Flask(__name__)

@app.route("/")
def fetch_url():
    url = sys.argv[1]
    if 'http://' not in url:
        url = 'http://' + url
    resp = requests.get(url)

    if resp.status_code == 200:
        return resp.text
    else:
        return f"Could not fetch html from '{url}'"

host = '0.0.0.0'
port = 5000
app.run(host=host, port=port)