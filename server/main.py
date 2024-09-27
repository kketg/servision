import datetime
from flask import Flask, Response, request, jsonify
from io import BytesIO
import base64
import os
import sys
import time
import json
from functools import wraps

from celery import Celery

import algorithms.sample as sample

import firebase_admin
from firebase_admin import credentials, auth

# Put an environment variable with the filename here
# cred = credentials.Certificate(...)
# firebase_admin.initialize_app(cred)

proc_dir = os.path.join("..", "PROC")
out_dir = os.path.join("..", "OUT")

with open(os.path.join("..","config.json"), "r") as f:
    config = json.loads(f.read())

for a in config["algorithms"]:
    if not os.path.exists(os.path.join(proc_dir, F"{a}")):
        os.makedirs(os.path.join(proc_dir, F"{a}"))
    if not os.path.exists(os.path.join(out_dir, F"{a}")):
        os.makedirs(os.path.join(out_dir, F"{a}"))

print(config)


app = Flask(__name__, static_folder="./templates/static")

app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/1'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

def convertBase64ToFile(base64str):
    file_bytes = base64.b64decode(base64str)
    file = BytesIO(file_bytes)
    return file


def check_token(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if not request.headers.get('authorization'):
            return {'message': 'No token provided'},400
        try:
            user = auth.verify_id_token(request.headers['authorization'])
            request.user = user
        except:
            return {'message':'Invalid token provided.'},400
        return f(*args, **kwargs)
    return wrap

@app.route("/")
@check_token
def index():
    return ""

@app.route("/status/<task_id>")
#@check_token
def check_status(task_id):
    task = process_task.AsyncResult(task_id)
    print(task)
    if task.state == "SUCCESS":
        task.forget()
    return task.state

@app.route("/vis/<algo>", methods = ['POST'])
#@check_token
def process(algo):
    if(request.method != "POST"):
        return jsonify(
            {
                "result": 1,
                "message": "Incorrect request type"
            }
        )
    if algo not in config["algorithms"]:
        return jsonify(
            {
                "result": 1,
                "message": "Incorrect media type"
            }
        )

    ts = datetime.datetime.fromtimestamp(time.time())
    uid = "SampleUser" #request.user["uid"]
    token = f"{algo}_{uid}_{ts}"
    bytes = request.get_data()
    store_path = os.path.join(proc_dir,f"{algo}",f"{token}.lrvb")
    with open(store_path, 'wb') as out:
        out.write(bytes)
    task = process_task.delay(token, algo, store_path)
    print("Task: " + str(task))
    return jsonify(
        {
            "result": 0, 
            "processing_call": token,
            "task_id": task.id,
            "message": "Successfully queued video"
        }
    )

@celery.task()
def process_task(token, algo, store_path):
    out_path = os.path.join(out_dir,f"{algo}",f"{token}.lrvb")
    match algo:
        # ideally the algorithms would be in the format of a separate file (i.e. squat), 
        # and run by a function called proc_call(token, store_path, out_path)
        case _:
            sample.proc_call(token, store_path, out_path)
    

if __name__ == "__main__":
   app.run(debug=True, port=config["port"])