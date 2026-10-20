from tempfile import TemporaryFile
from io import TextIOWrapper, BytesIO
import secrets
from time import time

import flask
from flask import request, jsonify
from flask_executor import Executor
from pdfmaker import process_csv

app = flask.Flask(__name__)
app.config['EXECUTOR_TYPE'] = 'process'
executor = Executor(app)

TOKEN_LENGTH = 12

MAX_WAITING_TIME = 10 * 60 # Ten minutes

UPLOAD_FILE_NAME = "file"
DOUBLESIDED_NAME = "doublesided"
COMBINE_NAME = "combine"

# NOTE: Because we store this in process memory, we can't run more than one WSGI worker.
# Make sure to configure the WSGI server to run this application entirely single-threaded.
# This isn't great, but it's a lot simpler and hence more maintainable than the alternative,
# and for software that most people use about twice a semester it's not worth setting up
# a whole Redis install or similar.
tasks = {}

@app.before_request
def purge_tasks():
    current_time = time()
    task_names = list(tasks.keys())
    for task_name in task_names:
        res, task_time = tasks[task_name]
        if current_time - task_time > MAX_WAITING_TIME:
            del tasks[task_name]

def task_render(in_file, doublesided, combine):
    in_file_text = TextIOWrapper(in_file, encoding="utf-8")
    out_file = BytesIO()
    process_csv(in_file_text, out_file, doublesided, combine)
    out_file.seek(0)
    return out_file, combine

@app.route("/start-render", methods=["POST"])
def start_render():
    if UPLOAD_FILE_NAME not in request.files:
        return "No file provided", 400
    
    in_file = BytesIO()
    request.files[UPLOAD_FILE_NAME].save(in_file)
    in_file.seek(0)

    form_args = map(lambda n: request.form.get(n) == "on", (DOUBLESIDED_NAME, COMBINE_NAME))

    task_name = secrets.token_urlsafe(TOKEN_LENGTH)
    while task_name in tasks: # Quick-and-dirty uniqueness enforcement
        task_name = secrets.token_urlsafe(TOKEN_LENGTH)
    def callback(future):
        tasks[task_name] = (future.result(), time())

    executor.submit(task_render, in_file, *form_args).add_done_callback(callback)

    return jsonify({"task_name": task_name})

@app.route("/check-render/<task_name>")
def check_render(task_name):
    return jsonify({"done": task_name in tasks})

@app.route("/get-render/<task_name>")
def get_render(task_name):
    if task_name not in tasks:
        return "This file is not available. The server only stores completed files for ten minutes, so it may have already been deleted.", 404
    
    (out_file, combine), _task_time = tasks[task_name]
    ext = "pdf" if combine else "zip"
    oneoff_file = BytesIO(out_file.getbuffer()) # Make a copy to send so that we can repeatedly send copies of the file until it times out -- Flask closes files after sending them
    return flask.send_file(oneoff_file, mimetype="application/{0}".format(ext), download_name="Printable.{0}".format(ext))

@app.route("/")
def frontpage():
    return flask.render_template("index.html")

if __name__ == "__main__":
    app.run()
