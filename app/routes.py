from app import app
from flask import render_template, send_from_directory, send_file, request, make_response, session
import hashlib
import io
import sys
import gzip
import json
import numpy as np
sys.path.append("/home/alex/Projects/CoffeeGPU/python/")
# sys.path.append("/home/alex/Projects/Aperture4/python/")
# from datalib, datalib_logsph import Data
import datalib as dl
import datalib_logsph as dl_sph
from app.integrate import integrate_fields_sphere

my_data = None

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

def compress_response(data):
    content = gzip.compress(json.dumps(data, cls=NumpyEncoder).encode('utf8'), 5)
    response = make_response(content)
    response.headers['Content-length'] = len(content)
    response.headers['Content-Encoding'] = 'gzip'
    return response

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

def compress_response(data):
    content = gzip.compress(json.dumps(data, cls=NumpyEncoder).encode('utf8'), 5)
    response = make_response(content)
    response.headers['Content-length'] = len(content)
    response.headers['Content-Encoding'] = 'gzip'
    return response

@app.route('/load_sph/<path:data_path>')
def load_sph_data(data_path):
    global my_data
    data_path = data_path.strip('"')
    hex_dig = hashlib.md5(data_path.encode()).hexdigest()
    my_data = dl_sph.Data(data_path)
    # print(hex_dig)
    return compress_response(my_data._conf)

@app.route('/load_cart/<path:data_path>')
def load_cart_data(data_path):
    global my_data
    data_path = data_path.strip('"')
    hex_dig = hashlib.md5(data_path.encode()).hexdigest()
    my_data = dl.Data(data_path)
    # print(hex_dig)
    return compress_response(my_data._conf)

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

@app.route('/fieldlines/<float:r_seed>/<int:num_seeds>')
def get_fieldlines(r_seed, num_seeds):
    global my_data
    # If data is not loaded then don't do anything
    if my_data is None:
        return compress_response(np.array([1,2,3,4,5]))
    else:
        lines = integrate_fields_sphere(r_seed, num_seeds, my_data)
        return compress_response(lines)
        # return

@app.route('/upload', methods = ['GET', 'POST'])
def upload():
    if request.method == 'POST':
        player_data = request.json["data"]
        return player_data
    else:
        return "Get method!"
