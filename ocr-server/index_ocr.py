from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import *

from flask import Flask
from flask import jsonify
from flask import url_for, redirect, send_from_directory, abort, render_template, request, make_response
from os.path import join, isfile, split, splitext, abspath, isdir
from os import makedirs
from glob import glob
from random import randrange

import os.path as op
import argparse
import ujson

import tinydb
from tinydb import Query

db = tinydb.TinyDB('index_manual.json')
# import catconv.operations as co
# import catconv.stabi as sb

parser = argparse.ArgumentParser()
parser.add_argument("json_path")
parser.add_argument("text_dict")
args = parser.parse_args()

app = Flask(__name__)


with open(args.json_path, 'rb') as jfile:
    catalog = ujson.load(jfile)

with open(args.text_dict, 'rb') as jfile:
    text = ujson.load(jfile)


page_dict = { page['path']: page for page in catalog['pages'] }
ordered_pages = sorted([page['path'] for page in page_dict.values()])

Page = Query()

for path, page in page_dict.items():
    batch, id = op.split(path)
    short_name = batch + id[4:]
    page['index_text'] = text[short_name]
    #if not db.contains(Page.name == page['path']):
        #entry = { 'text': page['index_text']} 
        #if len(page['lines']) > 0:
            #entry['index_name'] = page['lines'][0]['name']
        #db.insert(entry)

def getPageContext(name):
    page_context = {}
    page_context['next'] = ordered_pages[ordered_pages.index(name) + 1]
    print(page_context)
    return page_context

@app.route("/")
def route():
    return jsonify(catalog)

@app.route("/index.html")
def index():
    return render_template('catalog.html', pages=ordered_pages)

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
    return render_template('fix_page.html', page=page_dict[name], corr=db.search(Page.name == name), page_context=getPageContext(name))

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
    if line:
        img_path, image = op.join(catalog['path'], batch, id), line + '.bin.png'
    else: 
        img_path, image = op.join(catalog['path'], batch), id + '.png'
    print(img_path)
    return send_from_directory(img_path, image)


if __name__ == "__main__":
    app.run(debug=True)

