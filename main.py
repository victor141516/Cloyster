from config import (
    REDIS_HOST,
    REDIS_PORT,
    REDIS_DB,
    WEBS_DIR,
    KLOYSTER_SALT
)
from flask import Flask, request, redirect, make_response, abort, jsonify
from functools import wraps
import hashlib
from io import BytesIO
import logging
import os
from redpie import Redpie
from shutil import rmtree
from slugify import slugify
import zipfile


app = Flask('Cloyster', static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), WEBS_DIR))
db = Redpie(REDIS_DB, REDIS_HOST, REDIS_PORT)
LOGGER = logging.getLogger()

with open('static/upload.html', 'r') as f:
    upload_web_html = f.read()

with open('static/request_password.html', 'r') as f:
    request_password_html = f.read()


def admin(f):
    @wraps(f)
    def w(*args, **kwargs):
        if 'p' in request.cookies and 'admin' in db and request.cookies['p'] == db['admin']:
            return f(*args, **kwargs)
        else:
            return abort(401)
    return w


def get_size(path):
    total_size = 0
    if os.path.isdir(path):
        for dirpath, dirnames, filenames in os.walk(path):
            for fName in filenames:
                fp = os.path.join(dirpath, fName)
                total_size += os.path.getsize(fp)
        return total_size
    else:
        return os.path.getsize(path)


def unzip_to_webs_and_check(f, name):
    dest_dir = WEBS_DIR + '/' + name
    if os.path.isdir(dest_dir):
        return False

    buffer = BytesIO()
    buffer.write(f.stream.read())
    try:
        zf = zipfile.ZipFile(buffer)
    except zipfile.BadZipFile:
        return False

    try:
        zf.extractall(dest_dir)
    except Exception as e:
        LOGGER.error('Error extracting aparent good zip file', e)
        return False

    if os.path.exists(dest_dir + '/index.html'):
        return True
    else:
        rmtree(dest_dir)
        return False


def encode_p(p):
    return hashlib.sha256((p + KLOYSTER_SALT).encode('utf-8')).hexdigest()


@app.route('/', methods=['GET'])
def upload_web():
    return upload_web_html


@app.route('/', methods=['POST'])
def upload_web_post():
    if 'web_zip' not in request.files:
        return redirect(request.url)
    web_zip = request.files['web_zip']
    if not web_zip.filename.endswith('.zip'):
        return redirect(request.url)

    if 'password' not in request.form:
        return redirect(request.url)
    password = request.form['password']

    if 'web_name' not in request.form:
        return redirect(request.url)
    web_name = slugify(request.form['web_name'])

    is_ok = unzip_to_webs_and_check(web_zip, web_name)
    if not is_ok:
        return redirect(request.url)

    db[web_name] = encode_p(password)
    return redirect('/' + web_name)


@app.route('/setp', methods=['POST'])
def ser_cookie():
    response = redirect(request.form['path'])
    if 'password' in request.form:
        response.set_cookie('p', value=encode_p(request.form['password']))
    return response


@app.route('/<web_name>', defaults={'subpath': ''})
@app.route('/<web_name>/', defaults={'subpath': ''})
@app.route('/<web_name>/<path:subpath>')
def give_web(web_name, subpath):
    if 'p' in request.cookies \
        and web_name in db \
        and (request.cookies['p'] == db[web_name] or request.cookies['p'] == db['admin']):
        if os.path.isfile(WEBS_DIR + '/' + web_name + '/' + subpath):
            return app.send_static_file(web_name + '/' + subpath)
        elif os.path.isdir(WEBS_DIR + '/' + web_name + '/' + subpath):
            if os.path.isfile(WEBS_DIR + '/' + web_name + '/' + subpath + '/index.html'):
                return app.send_static_file(web_name + '/' + subpath + '/index.html')
            else:
                return abort(404)
        else:
            return abort(404)
    else:
        response = make_response(request_password_html)
        return response


@app.route('/api/web/list', methods=['GET'])
@admin
def list_webs():
    return jsonify(list(db))


@app.route('/api/web/<web>', methods=['GET', 'DELETE', 'PATCH'])
@admin
def get_web_size(web):
    if request.method == 'GET':
        return jsonify({'size': str(get_size(WEBS_DIR + '/' + web))})
    elif request.method == 'DELETE':
        if web in db:
            del(db[web])
        if os.path.exists(WEBS_DIR + '/' + web):
            rmtree(WEBS_DIR + '/' + web)
        return jsonify({'result': 'ok'})
    elif request.method == 'PATCH':
        password = request.json.get('password')
        if password:
            db[web] = encode_p(password)
            return jsonify({'result': 'ok'})
        return jsonify({'result': 'fail'})


if __name__ == "__main__":
    app.run('0.0.0.0', 12121, True)
