from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import *

from flask import Flask
from flask import jsonify
from flask import url_for, redirect, send_from_directory, abort, render_template, request
from os.path import join, isfile, split, splitext, abspath, isdir
from os import makedirs
from glob import glob
from random import randrange

import ocrolib

app = Flask(__name__)

# TODO: configuration with command line parameters
data_path = '../catalog-testset/SD/'
data_src = join(data_path, 'SD???????????.png')
data_files = glob(data_src)
file_ids = [splitext(split(p)[1])[0] for p in data_files] 

gt_path = '../catalog-gt/SD'

def remove_ext(name):
    return name[:name.index('.')]

def getFileNames(globList):
    return [ remove_ext(split(p)[1]) for p in globList]

def getSegmentTextPaths(idx):
    return glob(join(splitext(data_files[idx])[0], '??????.txt'))

def getSegments(idx):
    segPath = join(splitext(data_files[idx])[0], '??????.bin.png')
    return glob(segPath)

def getText(files):
    texts =  [open(p).read() for p in files]
    return dict(zip(getFileNames(files), texts))

@app.route("/")
def hello():
    return redirect(url_for('static' , filename='index.html'))

@app.route("/correct_random")
def routeToRandom():
    rnd_id = randrange(len(file_ids))
    return redirect(url_for("correct", file_id = file_ids[rnd_id]))

@app.route("/data/<file_id>/correction" , methods= ['GET', 'POST'])
def correct(file_id=None):
    if request.method == 'POST':
        for f in request.form:
            name, page_id, seg_id = f.split('_')
            text = request.form[f]
            # print(name, page_id, seg_id, text)
            gt_folder = join(gt_path, page_id)
            if not isdir(gt_folder):
                makedirs(abspath(gt_folder))
                print('create dir: ' + gt_folder)
            gt_file = join(gt_folder, seg_id + '.gt.txt')
            print(gt_file)
            with open(gt_file, 'w') as gt:
                gt.write(text)
    print('GET correct {}'.format(file_id))
    segments = getFileNames(glob(join(data_path,file_id, '??????.bin.png')))
    text = dict()
    for s in segments:
        gt_file = join(gt_path,file_id,s + '.gt.txt')
        ocr_file = join(data_path,file_id,s + '.txt')
        print(gt_file, isfile(gt_file))
        print(ocr_file, isfile(ocr_file))
        if isfile(gt_file):
            text[s] = open(gt_file).read()
        elif isfile(ocr_file):
            text[s] = open(ocr_file).read()
        else:
            text[s] = ''


    return render_template('view_card.html',
                           id=file_id, 
                           segments=segments,
                           texts=text,
                           datasource=None,
                           is_gt=False)


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
#    pseg = ocrolib.read_page_segmentation(binary_path(file_id))
#    regions = ocrolib.RegionExtractor()
#    regions.setPageLines(pseg)
    return jsonify(segments = list(range(0,len(getSegments(idx)))))

# TODO: serve static files 
@app.route("/data/<file_id>/segment/<seg_id>/png")
def getDataSegmentImage(file_id=None, seg_id=None):
    idx = int(file_ids.index(file_id))
    segments = getSegments(idx)
    segnames = [name for name in getFileNames(segments)]

    #if (idx >= 0) and (( 0 <= seg_id ) < len(segments)):
    print(segnames)
    segment_position = segnames.index(seg_id)
    if segment_position >= 0:
        return send_from_directory( *split(abspath(segments[segment_position]) ))
    else:
        print('wrong id: ', seg_id, segnames)
        return abort(404)


def binary_path(file_id):
    path = data_files[file_ids.index(file_id)]
    return str(splitext(path)[0] + u'.bin.png')


if __name__ == "__main__":
    app.run(debug=True)


