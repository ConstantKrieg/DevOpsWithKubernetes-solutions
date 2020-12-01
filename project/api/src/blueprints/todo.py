from flask import Blueprint, abort, request, jsonify, make_response, Response
from sqlalchemy import text, create_engine
import os

bp = Blueprint('todo', __name__)


db = os.environ['POSTGRES_DB']
user = os.environ['POSTGRES_USER']
password = os.environ['POSTGRES_PASSWORD']
engine = create_engine(f"postgresql://{user}:{password}@postgres-svc:5432/{db}")


def config(app):
    app.register_blueprint(bp)

@bp.route('/api/todo/', methods=(['GET']))
def get_todos():

    with engine.connect() as conn:
        stmt = text("SELECT * FROM todo")
        result = conn.execute(stmt)

        todo_list = result.fetchall()
        
        return jsonify(todos=[dict(row) for row in todo_list])


@bp.route('/api/todo/<int:todo_id>', methods=(['GET']))
def get_single_todo(todo_id):

    with engine.connect() as conn:
        stmt = text("SELECT * FROM todo WHERE id=:id")
        result = conn.execute(stmt, {'id': todo_id})

        row = result.fetchone()
        
        if 'content' in row:
            return jsonify(id=row['id'], todo=row['content'])
        else:
            abort(404)

@bp.route('/api/todo/', methods=(['POST']))
def add_todo():

    print("ADDING TODO", flush=True)
    content = request.json

    todo = content["todo"]

    if not todo or len(todo) > 140:
        abort(500)

    with engine.connect() as conn:
        stmt = text("INSERT INTO todo (content) VALUES (:content)")
        conn.execute(stmt, {'content': todo})

    return jsonify(todo=todo)

@bp.route('/api/todo/<int:todo_id>', methods=(['DELETE']))
def delete_todo(todo_id):
    with engine.connect() as conn:
        stmt = text("DELETE FROM todo WHERE id=:id")
        conn.execute(stmt, {'id': todo_id})

    return make_response(jsonify(success=True), 200)