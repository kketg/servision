import datetime
from flask import Flask, Response, request, jsonify, make_response, send_file
from werkzeug.utils import secure_filename
from io import BytesIO
import base64
import os
import sys
import time
import json
import mimetypes
from dotenv import load_dotenv

ALLOWED_EXTENSIONS = {"txt", "png", "mp4", "zip"}

load_dotenv()
port = int(os.environ.get("PORT"))

proc_dir = "PROC"
out_dir = "OUT"

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

flask = Flask(__name__)

@flask.route("/")
def index():
    return ""

@flask.route("/status")
def status():
    return jsonify({"result":0})

@flask.route("/update", methods=['POST'])
def update():
    algorithms = request.get_json()
    print(f"Algorithms Loaded: {algorithms}")
    for a in algorithms:
        if not os.path.exists(os.path.join(proc_dir, F"{a}")):
            os.makedirs(os.path.join(proc_dir, F"{a}"))
        if not os.path.exists(os.path.join(out_dir, F"{a}")):
            os.makedirs(os.path.join(out_dir, F"{a}"))
    return jsonify({"result":0})

@flask.route("/srv")
def serve_root(task_id: str):
    return "serve"

# Requires that full file is passed, as well as task id

@flask.route("/recv/proc/<id>", methods=['POST'])
def receive_proc_file(id: str):
    print(request.files)
    if 'file' not in request.files:
            return jsonify({
                "result": 1,
                "msg": "no file attached"
            })
    
    file = request.files["file"]
    if file.filename == '':
            return jsonify({
                "result": 1,
                "msg": "empty file attached"
            })
    
    fn = secure_filename(file.filename)

    if not allowed_file(fn):
         return jsonify({
              "result":1,
              "msg": "disallowed file type"
         })
    
    # splits off the parts of the filename
    split = fn.split("_")
    bytes = file.stream.read()

    if not os.path.exists(os.path.join(proc_dir,split[0])):
         return jsonify({
              "result":1,
              "msg": "algorithm not found"
         })

    # split[0] should represent the algorithm i.e. in sq_sample+user_(date) -> 'sq'
    with open(os.path.join(proc_dir,split[0],fn), "wb") as f:
        encoded = base64.b64encode(bytes)
        f.write(encoded)

    return jsonify({
        "result":0
    })


@flask.route("/recv/out/<id>", methods=['POST'])
def receive_out_file(id: str):
    if 'file' not in request.files:
            return jsonify({
                "result": 1,
                "msg": "no file attached"
            })
    
    mt = request.content_type
    file = request.files["file"]
    if file.filename == '':
            return jsonify({
                "result": 1,
                "msg": "empty file attached"
            })
    
    fn = secure_filename(file.filename)
    print(fn)
    if not allowed_file(fn):
         return jsonify({
              "result":1,
              "msg": "disallowed file type"
         })
    
    # splits off the parts of the filename
    split = fn.split("_")
    bytes = file.stream.read()

    if not os.path.exists(os.path.join(proc_dir,split[0])):
         return jsonify({
              "result":1,
              "msg": "algorithm not found"
         })

    # split[0] should represent the algorithm i.e. in sq_sample+user_(date) -> 'sq'
    with open(os.path.join(proc_dir,split[0],fn), "wb") as f:
        encoded = base64.b64encode(bytes)
        f.write(encoded)

    return jsonify({
        "result":0
    })


@flask.route("/srv/proc/<id>")
def serve_proc_file(id: str):
    mt = request.content_type
    ext = mimetypes.guess_extension(mt)
    split = id.split("_")[0]
    path = os.path.join(proc_dir,split[0],"UNPROC_"+id+ext)
    with open(path, "rb") as f:
        bytes = f.read()
        decoded = base64.b64decode(bytes)
    res = send_file(decoded,mt,False,id+ext)
    os.remove(path)
    return res


@flask.route("/srv/out/<id>")
def serve_out_file(id: str):
    mt = request.content_type
    ext = mimetypes.guess_extension(mt)
    split = id.split("_")[0]
    path = os.path.join(out_dir,split[0],id+ext)
    with open(path, "rb") as f:
        bytes = f.read()
        decoded = base64.b64decode(bytes)
    res = send_file(decoded,mt,False,id+ext)
    os.remove(path)
    return res

if __name__ == "__main__":
   flask.run(debug=True, port=port)