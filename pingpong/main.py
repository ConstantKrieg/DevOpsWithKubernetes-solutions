from flask import Flask, abort
from sqlalchemy import Table, MetaData, create_engine
import os

app = Flask(__name__)

pong_counter = 0

db = os.environ['POSTGRES_DB']
user = os.environ['POSTGRES_USER']
password = os.environ['POSTGRES_PASSWORD']
engine = None


@app.route('/')
def default_route():
    return "OK"


@app.route('/health')
def check_availability():
    global engine
    
    try:
        engine = create_engine(f"postgresql://{user}:{password}@postgres-svc.main-app:5432/{db}")
        engine.connect()
        init_db()
        return "OK"
    except:
        print("Failed to create engine")
        abort(500, "Database not up")


@app.route('/pingpong')
def pong():
    global engine

    if engine is None:
        abort(503, "Database not up")
    
    count = get_pong_count()
    with engine.connect() as conn:
        conn.execute("TRUNCATE pongs")
        conn.execute(f"INSERT INTO pongs (count) VALUES ({count + 1})")

    return f"pong {count + 1}"

@app.route('/pingpong/count')
def pong_count():
    
    count = get_pong_count()

    if count == -1:
        abort(503, "Database not up")

    return str(count)


def get_pong_count():

    if engine is None:
        return -1

    with engine.connect() as conn:
        result = conn.execute("SELECT * FROM pongs")
        

        row = result.fetchone()

        if 'count' in row:
            count = row['count']
            return count
        else:
            return 0



def init_db():
    global engine
    print('Initializing db', flush=True)
    engine = create_engine(f"postgresql://{user}:{password}@postgres-svc.main-app:5432/{db}")

    with engine.connect() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS pongs (
            count integer NOT NULL DEFAULT '0'
        )""")

        result = conn.execute("SELECT * FROM pongs")

        if result.fetchone() == None:
            print('Inserting pong count to the db')
            conn.execute("INSERT INTO pongs (count) VALUES (0)")


host = '0.0.0.0'
port = os.environ['PORT']
init_db()

if not port:
    port = 5000

app.run(host=host, port=int(port))