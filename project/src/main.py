from flask import Flask
import os
import sys

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    from blueprints import core
    core.config(app)

    return app




host = '0.0.0.0'
port = 5000
print("Server started on port %d" % port)
app = create_app()
app.run(host=host, port=port)
