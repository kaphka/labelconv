from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import *

from flask import Flask
from flask import Response
from flask import jsonify
from flask import url_for, redirect, send_from_directory, abort, render_template, request, make_response
from os.path import join, isfile, split, splitext, abspath, isdir
from os import makedirs
from glob import glob
import random
import re
from random import randrange

import os.path as op
import argparse
import ujson

import tinydb
from tinydb import Query

import pandas as pd

app = Flask(__name__)
DEFAULT_SEED = 'reproducibility'
SAMPLES = 400

def get_sample(catalog, N=SAMPLES, seed=DEFAULT_SEED):
    rnd = random.Random()
    rnd.seed(seed)
    print('sample seed: ', seed)
    lines = []
    for page in catalog['pages']:
        for line in page['lines']:
            lines.append(op.join(page['path'], line['name']))
    print(set([type(line) for line in lines]))
    lines = rnd.sample(sorted(lines), N)
    return lines


@app.route("/")
def route():
    return jsonify(catalog)


@app.route("/index.html")
def index():
    return render_template('catalog.html', pages=ordered_pages)


@app.route('/sample', methods=['POST'])
def post_sample_page():
    entry = request.get_json()
    if len(entry['gt']) == 0:
        print('no text')
    elif not text_lines.contains(Line.id == entry['id']):
        print('insert', entry)
        text_lines.insert(entry)
    else:
        print('update', entry)
        text_lines.update(entry, Line.id == entry['id'])
    return ('', 200)


@app.route('/sample/<name>', methods=['GET'])
def get_sample_page(name=None):
    print('get samples')
    text = {line['id']: line['gt'] for line in text_lines.all()}
    samples = get_sample(catalogs[name], seed=seed)
    return render_template('sample.html', sample=samples, text=text, name=name)


def getPageContext(name):
    page_context = {}
    page_context['next'] = ordered_pages[ordered_pages.index(name) + 1]
    print(page_context)
    return page_context


@app.route("/train/<batch>/<id>", methods=['GET'])
def get_page_fix_page(batch=None, id=None):
    name = op.join(batch, id)
    return render_template('fix_page.html',
                           page=page_dict[name],
                           corr=db.search(Page.name == name),
                           page_context=getPageContext(name))


@app.route("/train/<batch>/<id>", methods=['POST'])
def post_correction(batch=None, id=None):
    print(list(request.form.keys()))
    print(request.form['text'])
    entry = dict(request.form)

    name = op.join(batch, id)
    entry['name'] = name
    if not db.contains(Page.name == name):
        print('insert', str(entry))
        db.insert(entry)
    else:
        print('update', str(entry))
        db.update(entry, Page.name == name)
    return render_template('fix_page.html', page=page_dict[name], corr=db.search(Page.name == name),
                           page_context=getPageContext(name))

@app.route("/cat/<batch>/<id>/<line_name>")
def get_page(batch=None, id=None, line_name=None):
    name = op.join(batch, id)

    if line_name:
        line = [l for l in page_dict[name]['lines'] if l['name'] == line_name]
        return jsonify(line[0])
    return jsonify(page_dict[name])


@app.route("/image/<batch>/<id>/<line>")
@app.route("/image/<batch>/<id>")
def get_page_image(batch=None, id=None, line=None):
    cat_name = re.match('([A-S]+)', batch).group(0)
    if line:
        img_path, image = op.join(catalogs[cat_name]['path'], batch, id), line + '.png'
    else:
        img_path, image = op.join(catalogs[cat_name]['path'], batch), id + '.png'
    print(img_path)
    return send_from_directory(img_path, image)

parser = argparse.ArgumentParser()
parser.add_argument("json_path", help='json files that contain the lines')
# parser.add_argument("indices_path")
parser.add_argument("json_db", help='output path')
parser.add_argument("--seed", help='seed for random line selection')
args = parser.parse_args()

db = tinydb.TinyDB(args.json_db)
text_lines = db.table('lines')
db_samples = pd.DataFrame()
if args.seed:
    seed = args.seed
else:
    seed = DEFAULT_SEED

print("Seed: {}".format(seed))

catalogs  = {}
page_dict = {}
for json_path in glob(args.json_path):
    print("loading catalog file ", json_path)
    with open(json_path, 'rb') as jfile:
        catalog = ujson.load(jfile)
    print('with name', catalog['name'])
    page_dict.update({page['path']: page for page in catalog['pages']})
    catalogs[catalog['name']] = catalog
    print("Getting sample with '{}'".format(seed))
    db_samples = db_samples.append(get_sample(catalog, seed=seed))

db_samples.to_csv(op.join(op.dirname(args.json_db), 'sample_{}.csv'.format(seed)), )

print(catalogs.keys())

ordered_pages = sorted([page['path'] for page in page_dict.values()])

Page = Query()
Line = Query()

for path, page in page_dict.items():
    batch, id = op.split(path)
    short_name = batch + id[4:]


if __name__ == "__main__":
    app.run(debug=True)
