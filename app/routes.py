from flask import render_template, send_from_directory, send_file, request, make_response, session
from app import app
import hashlib
import io
import sys
import gzip
import json
import numpy as np
import app.datalib as dl
from app.integrate import get_fieldline, IntegrationThread
from app.gen_volume import VolumeThread

# my_data = None
data_path = ""
integration_thread = None
volume_thread = None
r_seed = 10.0
num_seeds = 200
seed_config = [{
    "name": "spherical_random",
    "r": r_seed,
    "n_seeds": num_seeds
}]

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

@app.route('/load_cart/<path:path>')
def load_cart_data(path):
    global integration_thread, seed_config, volume_thread, data_path
    data_path = path
    data_path = data_path.strip('"')
    hex_dig = hashlib.md5(data_path.encode()).hexdigest()
    my_data = dl.Data(data_path)
    integration_thread = IntegrationThread(seed_config, data_path)
    integration_thread.start()
    volume_thread = VolumeThread(data_path, 512)
    volume_thread.start()
    # print(hex_dig)
    return compress_response(my_data.fld_steps)


@app.route('/data/<path:path>')
def load_path(path):
    path = path.strip('"')
    #return data_path
    return render_template('index.html', data_path=path)


@app.route('/')
@app.route('/index')
def index():
    # return render_template('index.html', data_path="/home/alex/storage/Data/pulsar3d/dipole_60_paper")
    return load_path("/home/alex/storage/Data/pulsar3d/dipole_60_paper")


@app.route('/fieldlines/<int:step>/<float:r_seed>/<int:num_seeds>')
def get_fieldlines(step, r_seed, num_seeds):
    global seed_config, data_path
    # If data is not loaded then don't do anything
    # if my_data is None:
    #     return compress_response([])
    lines = get_fieldline(seed_config, data_path, step)
    return compress_response(lines)
        # return

@app.route('/config', methods = ['GET', 'POST'])
def config():
    global seed_config
    if request.method == 'POST':
        seed_config = request.json["config"]
        return seed_config
    else:
        return seed_config

@app.route('/progress_fieldline')
def progress_fieldline(thread_id):
    global integration_thread
    if integration_thread is None:
        return -1.0
    else:
        return integration_thread.progress

@app.route('/progress_volume')
def progress_volume(thread_id):
    global volume_thread
    if volume_thread is None:
        return -1.0
    else:
        return volume_thread.progress
