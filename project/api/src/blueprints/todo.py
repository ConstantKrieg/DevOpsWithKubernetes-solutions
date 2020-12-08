from flask import Blueprint, abort, request, jsonify, make_response, Response
from sqlalchemy import text, create_engine
import os

import asyncio
import json
from nats.aio.client import Client as NATS
from stan.aio.client import Client as STAN


bp = Blueprint('todo', __name__)


db = os.environ['POSTGRES_DB']
user = os.environ['POSTGRES_USER']
password = os.environ['POSTGRES_PASSWORD']
engine = create_engine(f"postgresql://{user}:{password}@postgres-svc:5432/{db}")


def config(app):
    app.register_blueprint(bp)

@bp.route('/api/todo/', methods=(['GET']))
def get_todos():

    try: 
        with engine.connect() as conn:
            stmt = text("SELECT * FROM todo")
            result = conn.execute(stmt)

            todo_list = result.fetchall()
        
            return jsonify(todos=[dict(row) for row in todo_list])
    except:
        abort(503, "Couldn't connect to database")

@bp.route('/api/todo/<int:todo_id>', methods=(['GET']))
def get_single_todo(todo_id):

    try:

        with engine.connect() as conn:
            stmt = text("SELECT * FROM todo WHERE id=:id")
            result = conn.execute(stmt, {'id': todo_id})

            row = result.fetchone()

            if 'content' in row:
                return jsonify(id=row['id'], todo=row['content'], done=row['done'])
            else:
                abort(404)
    except:
        abort(503, "Couldn't connect to database")


@bp.route('/api/todo/', methods=(['POST']))
def add_todo():

    print("ADDING TODO", flush=True)
    content = request.json

    todo = content["todo"]

    if not todo or len(todo) > 140:
        abort(500)

    try:
        with engine.connect() as conn:
            stmt = text("INSERT INTO todo (content, done) VALUES (:content, FALSE) RETURNING id")
            result = conn.execute(stmt, {'content': todo})
            row = result.fetchone()

            create_nats_msg(status="ADDED", todo=todo)

        return jsonify(id=row['id'],todo=todo)
    except Exception as e:
        print(e, flush=True)
        abort(503, "Couldn't connect to database")


@bp.route('/api/todo/<int:todo_id>', methods=(['DELETE']))
def delete_todo(todo_id):
    try:
        with engine.connect() as conn:
            stmt = text("DELETE FROM todo WHERE id=:id")
            conn.execute(stmt, {'id': todo_id})

        return make_response(jsonify(success=True), 200)
    except:
        abort(503, "Couldn't connect to database")

@bp.route('/api/todo/<int:todo_id>', methods=(['PUT']))
def mark_todo_as_finished(todo_id):
    try:
        with engine.connect() as conn:
            stmt = text("UPDATE todo SET done = TRUE WHERE id=:id")
            conn.execute(stmt, {'id': todo_id})

            gstmt = text("SELECT * FROM todo WHERE id=:id")
            result = conn.execute(gstmt, {'id': todo_id})
            row = result.fetchone()
            
            create_nats_msg(status="COMPLETED", todo=row['content'])


        return make_response(jsonify(success=True), 200)
    except Exception as e:
        print(e, flush=True)
        abort(503, "Couldn't connect to database")

def create_nats_msg(status, todo):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(publish_message(status, todo, loop))
    loop.close()

async def publish_message(status, todo, loop):
    nc = NATS()
 
    url = os.getenv("NATS_URL")
    print(url, flush=True)
    await nc.connect(servers=[url], loop=loop)
 
    await nc.publish("todos", json.dumps({"todo:": todo, "status": status }).encode())
    await nc.flush(1)
    await nc.close()
