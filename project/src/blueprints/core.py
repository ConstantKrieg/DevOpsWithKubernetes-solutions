from flask import Blueprint, render_template, send_from_directory
from datetime import date
import os
import glob
import requests
import shutil
import sys



IMAGE_PATH = '/images'

bp = Blueprint('core', __name__)

@bp.route('/test', methods=(['GET']))
def test_bp():
    return render_template('index.html', title="Kubernetes Project")


@bp.route('/daily_image')
def image_endpoint():
    get_image()
    d = date.today()
    
    filepath = f"{d.year}_{d.month}_{d.day}.jpg"
    return send_from_directory('/images/', filepath)

def get_image():
    global IMAGE_PATH

    d = date.today()
    
    filepath = f"{d.year}_{d.month}_{d.day}.jpg"
    
    full_filepath = os.path.join(IMAGE_PATH, filepath)
    if os.path.exists(full_filepath):
        return full_filepath
    else:
        clear_images()
        save_image(full_filepath)
        return full_filepath


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