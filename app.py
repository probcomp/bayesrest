import argparse
import json
import os
import sys

import flask
from flask import Flask, request
from flask_cors import CORS, cross_origin
import logging
import bayeslite

from iventure.utils_bql import cursor_to_df

from bayesdb_flask import *
from bayeslite import bayesdb_nullify

# To enable logging for flask-cors,
logging.getLogger('flask_cors').level = logging.DEBUG

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
app.debug = True

def set_bdb():
    os.path.realpath()

def get_bdb():
     assert hasattr(flask.g, 'bdb'), 'bayeslite .bdb file was not initialized on startup'

@app.route('/query', methods=['GET'])
@cross_origin(supports_credentials=True)
def query():
    table_name = 'test'
    query = simulate(table_name, 'Age')
    with flask.g.bdb.savepoint():
        cursor = flask.g.bdb.execute(query)
    return cursor_to_df(cursor).to_json()

@app.route('/predictive-relationship', methods=['POST'])
@cross_origin(supports_credentials=True)
def predictive_relationship():
    table_name = str(request.json['name'])
    column = str(request.json['column'])
    with flask.g.bdb.savepoint():
        flask.g.bdb.sql_execute(drop_dependence_probability_table(table_name))
        create = create_dependence_probability_table(table_name)
        flask.g.bdb.execute(create)
        query = select_dependence_probabilities(table_name, column)
        cursor = flask.g.bdb.execute(query)
        result = [row[0] for row in cursor]
    return json.dumps(result)

@app.route("/predict", methods=['post'])
@cross_origin(supports_credentials=True)
def predict():
    table_name = str(request.json['name'])
    row = request.json['row']
    column = str(request.json['column'])
    with flask.g.bdb.savepoint():
        query = infer_explicit_predict(table_name, column)
        cursor = flask.g.bdb.execute(query, [10, row])
        result = [row[0] for row in cursor]
    return json.dumps(result)

@app.route("/find-anomalies", methods=['post'])
@cross_origin(supports_credentials=True)
def find_anomalies():
    table_name = str(request.json['name'])
    target = str(request.json['target'])
    context = [str(x) for x in request.json['context']]
    with flask.g.bdb.savepoint():
        query = find_anomalies_query(table_name, target, context)
        cursor = flask.g.bdb.execute(query)
        result = [row[0] for row in cursor]
    return json.dumps(result)

def is_file(arg):
    """
    File 'type' for use with argparse. Raises an error of the argument is not
    the path to a valid file.

    """
    if not os.path.isfile(arg):
        raise argparse.ArgumentTypeError("{0} does not exist or is not a file".format(arg))
    else:
        return arg

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('bdb_file', nargs=1, type=is_file)
    args = parser.parse_args()
    flask.g.bdb = bayeslite.bayesdb_open(args.bdb_file)
    app.run(host='0.0.0.0', port=5000, debug=True)
