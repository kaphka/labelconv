from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import *

from flask import Flask
from flask import jsonify
from flask import url_for, redirect, send_from_directory, abort
from os.path import join, isfile, split, splitext, abspath
from glob import glob

import ocrolib

app = Flask(__name__)

# TODO: configuration with command line parameters
data_path = '../catalog-testset/SD/'
data_src = join(data_path, 'SD???????????.png')
data_files = glob(data_src)
file_ids = [splitext(split(p)[1])[0] for p in data_files] 


def getSegments(idx):
    segPath = join(splitext(data_files[idx])[0], '??????.bin.png')
    return glob(segPath)

@app.route("/")
def hello():
    return redirect(url_for('static' , filename='index.html'))

@app.route("/data/")
def getDataFiles():
    return jsonify(items = file_ids)

@app.route("/data/<file_id>")
def getDataFile(file_id=None):
    if file_id.endswith('.png'):
        print('serve file')
    path = join(data_path, file_ids) + '.png'
    print(path)
    return str(isfile(path))

# TODO: serve static files 
@app.route("/data/<file_id>/png")
def getDataImage(file_id=None):
    idx = file_ids.index(file_id)
    if idx >= 0:
        return send_from_directory( *split(abspath(data_files[idx]) ))

@app.route("/data/<file_id>/segments")
def getSegementData(file_id=None):
    idx = int(file_ids.index(file_id))
    pseg = ocrolib.read_page_segmentation(binary_path(file_id))
    regions = ocrolib.RegionExtractor()
    regions.setPageLines(pseg)
    return jsonify(segments = list(range(0,len(getSegments(idx)))))

# TODO: serve static files 
@app.route("/data/<file_id>/segment/<seg_id>/png")
def getDataSegmentImage(file_id=None, seg_id=None):
    idx = int(file_ids.index(file_id))
    segments = getSegments(idx)
    if (idx >= 0) and (( 0 <= seg_id ) < len(segments)):
        return send_from_directory( *split(abspath(segments[int(seg_id)]) ))
    else:
        print('wrong id')
        return abort(404)


def binary_path(file_id):
    path = data_files[file_ids.index(file_id)]
    return str(splitext(path)[0] + u'.bin.png')


if __name__ == "__main__":
    app.run(debug=True)


