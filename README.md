# DRPrinter

This is software built for the [UC Berkeley math Directed Reading Program](https://wp.math.berkeley.edu/drp/) that converts CSVs from application forms into printable PDFs.

## Installation

To install:

```
git clone <this repo>
pip install -r requirements.txt
```

To run in development mode:
```
flask run
```

This is a Flask app, so it expects to be hosted on a web server somewhere.  If you want to run your own instance, use [a production WSGI server](https://flask.palletsprojects.com/en/stable/deploying/) instead of Flask's own.