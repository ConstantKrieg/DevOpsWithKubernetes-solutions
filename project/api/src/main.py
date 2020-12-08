from flask import Flask, abort
import os
import sys
from sqlalchemy import create_engine, text


database_intialized = False


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    from blueprints.todo import config
    config(app)
    
    return app



def init_db():
    global database_intialized
    
    if database_intialized:
        return True
    
    db = os.environ['POSTGRES_DB']
    user = os.environ['POSTGRES_USER']
    password = os.environ['POSTGRES_PASSWORD']
    engine = create_engine(f"postgresql://{user}:{password}@postgres-svc:5432/{db}")
    print("in init db", flush=True)
    stmt = text("""CREATE TABLE IF NOT EXISTS todo (
            id SERIAL PRIMARY KEY,
            content varchar ( 140 ),
            done boolean
        )""")

    try:
        with engine.connect() as conn:
            conn.execute(stmt)
        
        database_intialized = True
        return True
    except Exception as e:
        print(str(e), flush=True)
        return False
    
    
host = '0.0.0.0'
port = 6000
#init_db()
app = create_app()

@app.route('/health')
def healtCheck():
    if init_db():
        return "OK"
    else:
        abort(500)
        
app.run(host=host, port=port)