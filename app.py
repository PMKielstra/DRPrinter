from tempfile import TemporaryFile
import io

import flask
from flask import request

from pdfmaker import process_csv

app = flask.Flask(__name__)

UPLOAD_FILE_NAME = "file"

@app.route("/")
def frontpage():
    return flask.render_template("index.html")

@app.route("/render", methods=["POST"])
def render():
    if UPLOAD_FILE_NAME not in request.files:
        return flask.redirect("/")
    in_file = request.files[UPLOAD_FILE_NAME]
    out_file = TemporaryFile()
    process_csv(io.TextIOWrapper(in_file, encoding="utf-8"), out_file)
    out_file.seek(0)
    return flask.send_file(out_file, mimetype="application/pdf", download_name="Printable.pdf")