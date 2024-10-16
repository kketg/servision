import datetime
from flask import Flask, Response, request, jsonify, make_response, send_file
from io import BytesIO
import base64
import os
import sys
import time
import json
from functools import wraps

from celery import Celery

import algorithms.sample as sample

import psycopg2

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


fl = Flask(__name__, static_folder="./templates/static")

fl.config['CELERY_BROKER_URL'] = 'redis://redis:6379/0'
fl.config['CELERY_RESULT_BACKEND'] = 'redis://redis:6379/1'

pg = psycopg2.connect(database="sv-jobs", user=config["pg-user"], password=config["pg-pass"], host="db", port="5432")

celery = Celery(f"{fl.name}.celery", broker=fl.config['CELERY_BROKER_URL'])
celery.conf.update(fl.config)

# Meant to convert base64 encoded data from requests into the media files they represent
def convert_base64_to_file(base64str):
    file_bytes = base64.b64decode(base64str)
    file = BytesIO(file_bytes)
    return file

def read_file_to_base64(path):
    with open(path, "rb") as f:
        b = f.read()
    return base64.b64encode(b)


# Checks request for valid firebase authentication token
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

@fl.route("/")
#@check_token
def index():
    return ""

# Checks if a certain task is finished or not, and if it is returns the data
@fl.route("/status/<task_id>")
#@check_token
def check_status(task_id: str):
    task_username = task_id.split("_")[0]
    # if request.user["uid"] != task_username:
    #     return jsonify(
    #         {
    #             "result": 1,
    #             "message": "Unauthorized status check"
    #         }
    #     )
    task = process_task.AsyncResult(task_id)
    print(task)
    return task.state

@fl.route("/download/<task_id>")
#@check_token
def download_file(task_id: str):
    task_username = task_id.split("_")[0]
    if request.user["uid"] != task_username:
        return jsonify(
            {
                "result": 1,
                "message": "Unauthorized download"
            }
        )
    task = process_task.AsyncResult(task_id)
    if task.state == "SUCCESS":
        result = task.get()
        # Here is where the has_next should be done. Each job should have a postgres entry with the token as the key
        # It should contain a list of all the files to be downloaded, and this shouldn't mark the task for deletion 
        # until all of them are downloaded
        f_bytes = read_file_to_base64(result)
        # Going to need to add other attributes like mimetype, download_name, etc
        return send_file(f_bytes)

@fl.route("/status/output/<algo>")
def check_output(algo: str):
    if algo not in config["algorithms"]:
        return jsonify(
            {
                "result": 1,
                "message": "Incorrect media type"
            }
        )
    return jsonify(
        {
            "result": 0,
            "data": os.listdir(os.path.join(out_dir, algo))
        }
    )
        

# Root request for calling any of the algorithms
@fl.route("/vis/<algo>", methods = ['POST'])
#@check_token
def process(algo: str):
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
    # Do a check here to make sure the user exists in firebase, 
    # and that the given token authorizes this specific user
    token = f"{algo}_{uid}_{ts}"
    # later on this should be decoded from base64, as binary data sent from the client should be in base64
    bytes = request.get_data() #convert_base64_to_file(request.get_data())
    
    store_path = os.path.join(proc_dir,f"{algo}",f"{token}.lrvb")
    with open(store_path, 'wb') as out:
        out.write(bytes)
    # Creates a celery task to be completed by a worker
    task = process_task.delay(token, algo, store_path)
    # PUT A POSTGRES INSERT STATEMENT HERE
    print("Task Queued: " + str(task))
    return jsonify(
        {
            "result": 0, 
            "proc_call": token,
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
    return out_path
    

if __name__ == "__main__":
   fl.run(debug=True, port=config["port"])