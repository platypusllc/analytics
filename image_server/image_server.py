from ipyleaflet import Map, ImageOverlay, Polyline
import matplotlib
import matplotlib.cm
from matplotlib import pyplot
import numpy as np
import numpy.lib.recfunctions
import scipy
import scipy.interpolate
import pandas
import platypus.io.logs
import os
import uuid
import glob
import flask
from flask import send_from_directory, render_template
import json

UPLOAD_FOLDER = '/home/shawn/data/ERM/log_files/'
ALLOWED_EXTENSIONS = set(['txt'])

from flask import Flask
app = Flask(__name__, static_url_path='', )

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

class PlatypusDataStore(object):
    """docstring for PlatypusDataStore"""
    def __init__(self, data):
        super(PlatypusDataStore, self).__init__()
        self.data = data


@app.route('/overlay/<path:filename>')
def serve_static(filename):
    print "getting static file: ", filename, "from dir: ",os.path.join(".", 'overlay')
    return send_from_directory(os.path.join(".", 'overlay'), filename)

# @app.route('/overlay/<path:path>')
# def send(path):
#     path = "/overlay/"+path
#     if (os.path.exists("./"+path)):
#         print "sending file: " + path
#         return send_from_directory("overlay", path)
#     else:
#         print path +" does not exist"

def sensor_id_to_name(id):
    if (id == 0):
        # Select the sensor and the name of the channel for that sensor.
        sensor_name = 'PH_ATLAS'
        sensor_channel = 'ph'
        sensor_units = "pH"
    elif (id == 1):
        sensor_name = 'EC_DECAGON'
        sensor_channel = 'ec'
        sensor_units = 'Electrical Conductivity (uS/cm)'
    elif (id == 2):
        sensor_name = 'T_DECAGON'
        sensor_channel = 'temperature'
        sensor_units = 'Temperature (C)'
    elif (id == 3):
        sensor_name = 'DO_ATLAS'
        sensor_channel = 'do'
        sensor_units = 'Turbidty (NTU)'

    return (sensor_name, sensor_channel, sensor_units)

@app.route('/logs/<string:log_file>/<int:sensor_id>')
def render_page(log_file, sensor_id):
    print "rendering log file page from stats"
    # open stats file for this log
    with open("./stats/"+log_file+'.json', 'r') as readfile:
        data = json.load(readfile)
        print data
    data = data[str(sensor_id)]

    print data
    data["bar_filename"] = "/overlay/"+data["bar_filename"]
    data["overlay_filename"] = "/overlay/"+data["overlay_filename"]
    (sensor_name, sensor_channel, sensor_units) = sensor_id_to_name(sensor_id)
    return render_template('render.html', log_file = log_file, data_bounds = data["data_bounds"], bar = data["bar_filename"], map_overlay = data["overlay_filename"], data_min = data["data_min"], data_max = data["data_max"], sensor_name = sensor_name)

@app.route('/index')
@app.route('/')
def render_index():
    log_folder = "/home/shawn/data/ERM/log_files/"
    log_files = []
    for file in os.listdir(log_folder):
        if (os.path.isfile(log_folder+file)):
            print "adding file: " + file
            log_files.append(os.path.splitext(file)[0])
        else:
            print(file +" is not a file")

    log_files.sort()
    print log_files

    return render_template('index.html', log_folder = log_folder, log_files = log_files)

def root_dir():  # pragma: no cover
    return os.path.abspath(os.path.dirname(__file__))

if __name__ == '__main__':
    app.run()