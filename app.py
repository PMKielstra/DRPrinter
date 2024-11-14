from tempfile import TemporaryFile
import io

import flask
from flask import request, jsonify
from flask_executor import Executor
from pdfmaker import process_csv

app = flask.Flask(__name__)
executor = Executor(app)

UPLOAD_FILE_NAME = "file"
RENDER_TASK_NAME = "pdf_render"

def task_render(in_file):
    out_file = TemporaryFile()
    process_csv(io.TextIOWrapper(in_file, encoding="utf-8"), out_file)
    in_file.close()
    out_file.seek(0)
    return out_file

@app.route("/")
def frontpage():
    return flask.render_template("index.html")

@app.route("/start-render", methods=["POST"])
def start_render():
    if UPLOAD_FILE_NAME not in request.files:
        return flask.redirect("/")
    in_file = TemporaryFile()
    request.files[UPLOAD_FILE_NAME].save(in_file)
    in_file.seek(0)
    executor.submit_stored(RENDER_TASK_NAME, task_render, in_file)
    return {}

@app.route("/get-render")
def get_render():
    if not executor.futures.done(RENDER_TASK_NAME):
        return jsonify({"waiting": True})
    out_file = executor.futures.pop(RENDER_TASK_NAME).result()
    return flask.send_file(out_file, mimetype="application/pdf", download_name="Printable.pdf")

if __name__ == "__main__":
    app.run()
