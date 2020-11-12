import string
import time
import random
import datetime
from flask import Flask


app = Flask(__name__)

letters = string.ascii_letters
s = ''.join(random.choice(letters) for i in range(25))

@app.route("/")
def get_string():
    timestamp = ''
    pongs = ''
    with open('/files/timestamp.txt', 'r') as f:
        timestamp = f.read()

    with open('/files/pongs.txt', 'r') as pf:
        pongs = pf.read()
    
    return f"{timestamp} {s} \n Ping / Pongs: {pongs}"

if __name__ == "__main__":
    host = '0.0.0.0'
    port = 5000
    app.run(host=host, port=port)