from flask import Flask
from sqlalchemy import Table, MetaData, create_engine
import os

app = Flask(__name__)

pong_counter = 0

db = os.environ['POSTGRES_DB']
user = os.environ['POSTGRES_USER']
password = os.environ['POSTGRES_PASSWORD']
engine = create_engine(f"postgresql://{user}:{password}@postgres-svc.main-app:5432/{db}")


@app.route('/')
def default_route():
    return "OK"

@app.route('/pingpong')
def pong():
    count = get_pong_count()
    with engine.connect() as conn:
        conn.execute("TRUNCATE pongs")
        conn.execute(f"INSERT INTO pongs (count) VALUES ({count + 1})")

    return f"pong {count + 1}"

@app.route('/pingpong/count')
def pong_count():
    return str(get_pong_count())


def get_pong_count():
    with engine.connect() as conn:
        result = conn.execute("SELECT * FROM pongs")
        

        row = result.fetchone()

        if 'count' in row:
            count = row['count']
            return count
        else:
            return 0



def init_db():
    print('Initializing db')
    

    with engine.connect() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS pongs (
            count integer NOT NULL DEFAULT '0'
        )""")

        result = conn.execute("SELECT * FROM pongs")

        if result.fetchone() == None:
            print('Inserting pong count to the db')
            conn.execute("INSERT INTO pongs (count) VALUES (0)")


host = '0.0.0.0'
port = 5000
init_db()
app.run(host=host, port=port)