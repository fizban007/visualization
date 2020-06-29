from app import app
from flask import render_template, send_from_directory, send_file, request, make_response, session
import hashlib
import io
import sys
import gzip
import json
import numpy as np
import app.datalib as dl
from app.integrate import get_fieldline, IntegrationThread

my_data = None
my_thread = None
r_seed = 10.0
num_seeds = 200
seed_config = {
    "name": "spherical_random",
    "r": r_seed,
    "n_seeds": num_seeds
}

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

# @app.route('/load_sph/<path:data_path>')
# def load_sph_data(data_path):
#     global my_data
#     data_path = data_path.strip('"')
#     hex_dig = hashlib.md5(data_path.encode()).hexdigest()
#     my_data = dl_sph.Data(data_path)
#     # print(hex_dig)
#     return compress_response(my_data.fld_steps)

@app.route('/load_cart/<path:data_path>')
def load_cart_data(data_path):
    global my_data, my_thread, seed_config
    data_path = data_path.strip('"')
    hex_dig = hashlib.md5(data_path.encode()).hexdigest()
    my_data = dl.Data(data_path)
    my_thread = IntegrationThread(seed_config, my_data)
    my_thread.start()
    # print(hex_dig)
    return compress_response(my_data.fld_steps)

@app.route('/data/<path:data_path>')
def load_path(data_path):
    data_path = data_path.strip('"')
    #return data_path
    return render_template('index.html', data_path=data_path)

@app.route('/')
@app.route('/index')
def index():
    # return render_template('index.html', data_path="/home/alex/storage/Data/pulsar3d/dipole_60_paper")
    return load_path("/home/alex/storage/Data/pulsar3d/dipole_60_paper")

@app.route('/fieldlines/<int:step>/<float:r_seed>/<int:num_seeds>')
def get_fieldlines(step, r_seed, num_seeds):
    global my_data, seed_config
    # If data is not loaded then don't do anything
    if my_data is None:
        return compress_response([])
    else:
        my_data.load(step)
        lines = get_fieldline(seed_config, my_data, step)
        return compress_response(lines)
        # return

@app.route('/upload', methods = ['GET', 'POST'])
def upload():
    if request.method == 'POST':
        player_data = request.json["data"]
        return player_data
    else:
        return "Get method!"

@app.route('/progress')
def progress(thread_id):
    global my_thread
    if my_thread is None:
        return -1.0
    else:
        return my_thread.progress
