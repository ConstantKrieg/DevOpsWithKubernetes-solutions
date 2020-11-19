from flask import Flask
import os
import sys
from sqlalchemy import create_engine, text



def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    from blueprints.todo import config
    config(app)
    

    return app

def init_db():
    db = os.environ['POSTGRES_DB']
    user = os.environ['POSTGRES_USER']
    password = os.environ['POSTGRES_PASSWORD']
    engine = create_engine(f"postgresql://{user}:{password}@postgres-svc.project:5432/{db}")

    stmt = text("""CREATE TABLE IF NOT EXISTS todo (
            id SERIAL PRIMARY KEY,
            content varchar ( 140 )
        )""")

    with engine.connect() as conn:
        conn.execute(stmt)
    
    
host = '0.0.0.0'
port = 6000
init_db()
app = create_app()
app.run(host=host, port=port)