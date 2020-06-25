from app import app
from flask import render_template, send_from_directory, send_file, request
import hashlib
import io
import sys
import gzip
import json
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
    content = gzip.compress(json.dumps(data._conf).encode('utf8'), 5)
    response = make_response(content)
    response.headers['Content-length'] = len(content)
    response.headers['Content-Encoding'] = 'gzip'
    return response

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

@app.route('/upload', methods = ['GET', 'POST'])
def upload():
    if request.method == 'POST':
        player_data = request.json["data"]
        return player_data
    else:
        return "Get method!"
