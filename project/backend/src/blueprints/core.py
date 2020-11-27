from flask import Blueprint, render_template, send_from_directory, request, abort, jsonify
from datetime import date
import os
import glob
import requests
import shutil
import sys
import json


IMAGE_PATH = '/images'

bp = Blueprint('core', __name__)

@bp.route('/', methods=(['GET']))
def test_bp():
    r = requests.get('http://kflask-api-svc.project/api/todo/')
    print("IN NEW IMAGE")
    if r.status_code != 200:
        print("Error when loading todos", r.status_code, flush=True)
        todos = []
    else:
        todos = r.json()


    return render_template('index.html', title="Kubernetes Project", todos=todos)

@bp.route('/new_todo', methods=(['POST']))
def post_todo():
    content = request.json
    todo = content["todo"]

    r = requests.post('http://kflask-api-svc.project/api/todo/', json={'todo': todo})
    print(r, flush=True)
    if r.status_code != 200:
        abort(r.status_code)
    
    return r.json()
    

@bp.route('/daily_image', methods=(['GET']))
def image_endpoint():
    filepath = get_image()
    d = date.today()
    
    return send_from_directory('/images/', filepath)

def get_image():
    global IMAGE_PATH

    d = date.today()
    print('In newer image')
    
    filepath = f"{d.year}_{d.month}_{d.day}.jpg"
    
    full_filepath = os.path.join(IMAGE_PATH, filepath)
    if os.path.exists(full_filepath):
        return filepath
    else:
        clear_images()
        save_image(full_filepath)
        return filepath


def clear_images():
    global IMAGE_PATH

    if os.path.exists(IMAGE_PATH):

        files = glob.glob(IMAGE_PATH)
        for f in files:
            if (os.path.isdir(f)):
                pass
            else:
                os.remove(f)


def save_image(filepath):

    img_url = 'https://picsum.photos/1200'
    resp = requests.get(img_url, stream=True)
    with open(filepath, 'wb') as f:
        print('Writing image to', filepath, flush=True)
        shutil.copyfileobj(resp.raw, f)
    
    del resp



def config(app):
    app.register_blueprint(bp)