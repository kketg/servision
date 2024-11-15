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
from functools import wraps

ALLOWED_EXTENSIONS = {'txt', 'png', "mp4"}

proc_dir = "PROC"
out_dir = "OUT"
with open(os.path.join("..","config.json"), "r") as f:
    config = json.loads(f.read())

for a in config["algorithms"]:
    if not os.path.exists(os.path.join(proc_dir, F"{a}")):
        os.makedirs(os.path.join(proc_dir, F"{a}"))
    if not os.path.exists(os.path.join(out_dir, F"{a}")):
        os.makedirs(os.path.join(out_dir, F"{a}"))


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

flask = Flask(__name__)

@flask.route("/")
def index():
    return ""

@flask.route("/srv")
def serve_root(task_id: str):
    return "serve"

# Requires that full file is passed, as well as task id
methods=['POST']
@flask.route("/recv/proc/<id>")
def receive_file(id: str):
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
    if not allowed_file(fn):
         return jsonify({
              "result":1,
              "msg": "disallowed file type"
         })
    # splits off the parts of the filename
    split = fn.split("_")
    bytes = file.stream.read()
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
    with open(os.path.join(proc_dir,split[0],"UNPROC_"+id+ext), "rb") as f:
        bytes = f.read()
        decoded = base64.b64decode(bytes)
    return send_file(decoded,mt,False,id+ext)

@flask.route("/srv/out/<id>")
def serve_out_file(id: str):
    mt = request.content_type
    ext = mimetypes.guess_extension(mt)
    split = id.split("_")[0]
    with open(os.path.join(out_dir,split[0],id+ext), "rb") as f:
        bytes = f.read()
        decoded = base64.b64decode(bytes)
    return send_file(decoded,mt,False,id+ext)