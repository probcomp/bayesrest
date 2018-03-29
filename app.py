import argparse
import json
import os

import flask
from flask import Flask, request
from flask_cors import CORS, cross_origin
import logging
import bayeslite

from iventure.utils_bql import cursor_to_df

from bayesdb_flask import *
from bayeslite import bayesdb_nullify
from bayeslite.backends.cgpm_backend import CGPM_Backend

# To enable logging for flask-cors,
logging.getLogger('flask_cors').level = logging.DEBUG

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
app.debug = True

def get_bdb():
    if app.config['BDB_FILE'] is None:
        raise RuntimeError('BDB_FILE was not set')
    if not hasattr(flask.g, 'bdb'):
        flask.g.bdb = bayeslite.bayesdb_open(pathname=app.config['BDB_FILE'], builtin_backends=False)
        cgpm_backend = CGPM_Backend({}, multiprocess=False)
        bayeslite.bayesdb_register_backend(flask.g.bdb, cgpm_backend)
    return flask.g.bdb

@app.route('/heartbeat', methods=['GET'])
@cross_origin(supports_credentials=True)
def heartbeat():
    get_bdb()
    return 'OK'

@app.route('/query', methods=['GET'])
@cross_origin(supports_credentials=True)
def query():
    table_name = 'test'
    query = simulate(table_name, 'Age')
    bdb = get_bdb()
    with bdb.savepoint():
        cursor = bdb.execute(query)
    return cursor_to_df(cursor).to_json()

@app.route('/predictive-relationship', methods=['POST'])
@cross_origin(supports_credentials=True)
def predictive_relationship():
    table_name = str(request.json['name'])
    column = str(request.json['column'])
    bdb = get_bdb()
    with bdb.savepoint():
        bdb.sql_execute(drop_dependence_probability_table(table_name))
        create = create_dependence_probability_table(table_name)
        bdb.execute(create)
        query = select_dependence_probabilities(table_name, column)
        cursor = bdb.execute(query)
        result = [row[0] for row in cursor]
    return json.dumps(result)

@app.route("/predict", methods=['post'])
@cross_origin(supports_credentials=True)
def predict():
    table_name = str(request.json['name'])
    row = request.json['row']
    column = str(request.json['column'])
    bdb = get_bdb()
    with bdb.savepoint():
        query = infer_explicit_predict(table_name, column)
        cursor = bdb.execute(query, [10, row])
        result = [row[0] for row in cursor]
    return json.dumps(result)

@app.route("/find-anomalies", methods=['post'])
@cross_origin(supports_credentials=True)
def find_anomalies():
    #  table_name = str(request.json['name'])
    table_name = "satellites_full"
    target = str(request.json['target'])
    context = [str(x) for x in request.json['context']]
    bdb = get_bdb()
    with bdb.savepoint():
        query = find_anomalies_query(table_name, target, context)
        print query
        cursor = bdb.execute(query)
        result = [row[0] for row in cursor]
        print result
    return json.dumps(result)

@app.route("/find-peers", methods=['post'])
@cross_origin(supports_credentials=True)
def find_peers():
    table_name = "satellites_full"
    target = str(request.json['target'])
    context = [str(x) for x in request.json['context']]
    bdb = get_bdb()
    with bdb.savepoint():
        query = find_peer_rows_query(table_name, target, context)
        print query
        cursor = bdb.execute(query)
        result = [[row[0], row[1]] for row in cursor]
        print result
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
    (bdb_file,) = args.bdb_file
    app.config.update(dict(BDB_FILE=bdb_file))
    app.run(host='0.0.0.0', port=5000, debug=True)
