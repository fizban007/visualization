from app import app
from flask import render_template, send_from_directory, send_file
import hashlib
import io
import sys
sys.path.append("/home/alex/Projects/CoffeeGPU/python/")
# sys.path.append("/home/alex/Projects/Aperture4/python/")
from datalib import Data

data = None

@app.route('/load_sph/<path:data_path>')
def load_sph_data(data_path):
    data_path = data_path.strip('"')
    hex_dig = hashlib.md5(data_path.encode()).hexdigest()
    data = Data(data_path)
    # print(hex_dig)
    return data._conf

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/data/<filename>')
def get_data(filename):
    print(filename)
    with open('data/' + filename, 'rb') as f:
        return send_file(io.BytesIO(f.read()),
                         mimetype = "application/binary")

@app.route('/fieldlines/<int:step>')
def get_fieldlines(step):
    # If data is not loaded then don't do anything
    if data is None:
        return None
