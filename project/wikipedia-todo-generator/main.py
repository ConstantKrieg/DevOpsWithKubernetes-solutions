import requests
from sqlalchemy import create_engine, text
import os


db = os.environ['POSTGRES_DB']
user = os.environ['POSTGRES_USER']
password = os.environ['POSTGRES_PASSWORD']
engine = create_engine(f"postgresql://{user}:{password}@postgres-svc.project:5432/{db}")


resp = requests.get('https://en.wikipedia.org/wiki/Special:Random')

with engine.connect() as conn:
    stmt = text("INSERT INTO todo (content) VALUES (:content)")
    conn.execute(stmt, {'content': f"Remember to read {resp.url}"})