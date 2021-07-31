from flask import (Flask, request, render_template, send_file, send_from_directory,
jsonify, url_for, redirect, json)
from werkzeug.exceptions import HTTPException
from markupsafe import escape
from os.path import dirname, join
from os import listdir, remove
from datetime import datetime
from werkzeug.utils import secure_filename
from main import *
from dotenv import dotenv_values

app = Flask(__name__)

print(datetime.now())
config = dotenv_values(".env")
foldername = config.get('EXCEL')
PORT = config.get('PORT')

PATH = join(dirname(__file__),f'{foldername}/')
print(PATH)

@app.route('/')
def index():
    onlyfiles = [f for f in listdir(PATH) if '$' not in f]
    onlyexcel = [f for f in onlyfiles if 'xlsx' in f]
    onlyfiles.sort()
    context = {
        'file': onlyexcel,
        'day': str(datetime.now().date()),
        'test': 'sdfdfdsf'
    }
    return render_template('home.html', **context)

@app.route('/delete/<file>', methods=['DELETE'])
def delete(file):
    if request.method == 'DELETE':
        remove(join(PATH,file))
        return "deleted"

def upload():
    f = request.files.getlist('excel_file')
    filenames = []
    day = datetime.now().date().strftime('%d-%m-%Y')
    for i in f:
        filename = f'{day}_{i.filename}'
        i.save(PATH+filename)
        filenames.append(filename)
    return filenames

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        upload()
        return redirect(url_for('index'))

@app.route('/uploadcheck', methods=['POST'])
def uploadcheck():
    if request.method == 'POST':
        f = upload()
        print(f)
        redirect(url_for('index'))
        return checkAll(f)

@app.route("/excel/<file>")
def download(file):
    return send_file(PATH+file)

# @app.route('/file')
# def pdf():
#     return send_from_directory(dirname(__file__)+'/testfile/', 'Amongus.pdf')

def checkAll(f):
    result = checkMany(f)
    return render_template('check.html', result = result)

from pprint import pprint
@app.route('/check', methods=['POST'])
def checkAllController():
    if request.method == 'POST':
        report = []
        f = request.form.getlist('checkfile')
        print(f)
        return checkAll(f)
        # return redirect(url_for('check'))

@app.route('/check/<name>')
def checkByNameController(name):
    result = checkOneppl(name)
    return render_template('deepcheck.html', result = result)


# @app.errorhandler(404)
# def page_not_found(error):
#     return 'This page does not exist', 404

# @app.errorhandler(HTTPException)
# def handle_exception(e):
#     """Return JSON instead of HTML for HTTP errors."""
#     # start with the correct headers and status code from the error
#     response = e.get_response()
#     # replace the body with JSON
#     response.data = json.dumps({
#         "code": e.code,
#         "name": e.name,
#         "description": e.description,
#     })
#     response.content_type = "application/json"
#     return response


if __name__ == '__main__':
    app.run(port = PORT, debug=True)

# app.run(debug=True)