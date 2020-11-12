from flask import Flask

app = Flask(__name__)

pong_counter = 0

@app.route('/pingpong/')
def pong():
    global pong_counter

    pong_counter += 1
    s = ''
    
    with open('/files/pongs.txt', 'w') as f:
        f.write(str(pong_counter))

    with open('/files/pongs.txt', 'r') as f:
        s = f.read()
    
    return f"pong {s}"


host = '0.0.0.0'
port = 5000
app.run(host=host, port=port)