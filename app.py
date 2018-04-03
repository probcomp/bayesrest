import argparse
import json
import os

import flask
from flask import Flask, request
from flask.json import jsonify
from flask_cors import CORS, cross_origin
import logging
import bayeslite

from iventure.utils_bql import cursor_to_df

from bayesdb_flask import *
from bayeslite import bayesdb_nullify
from bayeslite.backends.cgpm_backend import CGPM_Backend

# To enable logging for flask-cors,

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
app.debug = True

def get_bdb():
    if not 'BDB_FILE' in app.config:
        raise RuntimeError('BDB_FILE was not set')
    if not 'bdb' in flask.g:
        app.logger.info('instantiating a new bdb')
        flask.g.bdb = bayeslite.bayesdb_open(pathname=app.config['BDB_FILE'], builtin_backends=False)
        cgpm_backend = CGPM_Backend({}, multiprocess=False)
        bayeslite.bayesdb_register_backend(flask.g.bdb, cgpm_backend)
    return flask.g.bdb

def set_last_query(query):
    bdb = get_bdb()
    quoted_query = json.dumps(query)
    with bdb.savepoint():
        bdb.sql_execute(create_last_query_table_query())
        bdb.sql_execute(set_last_query_query(), [quoted_query])

def get_last_query():
    bdb = get_bdb()
    with bdb.savepoint():
        bdb.sql_execute(create_last_query_table_query())
        cursor = bdb.sql_execute(get_last_query_query())
    return json.loads(cursor.fetchone()[0])

def sql_execute(bdb, query, *args):
    set_last_query(query)
    app.logger.info('sql executing query: %s', query)
    return bdb.sql_execute(query, *args)

def execute(bdb, query, *args):
    set_last_query(query)
    app.logger.info('executing query: %s', query)
    return bdb.execute(query, *args)

def init_last_query():
    bdb = get_bdb()
    with bdb.savepoint():
        for query in create_last_query_table_queries():
            sql_execute(bdb, query)

@app.route('/heartbeat', methods=['GET'])
@cross_origin(supports_credentials=True)
def heartbeat():
    get_bdb()
    settings = ['BDB_FILE', 'LOG_LEVEL']
    return jsonify({key: app.config[key] for key in settings})

@app.route('/last-query', methods=['GET'])
@cross_origin(supports_credentials=True)
def last_query():
    return jsonify({'last_query': get_last_query()})

@app.route('/query', methods=['GET'])
@cross_origin(supports_credentials=True)
def query():
    table_name = 'test'
    query = simulate(table_name, 'Age')
    bdb = get_bdb()
    with bdb.savepoint():
        cursor = execute(bdb, query)
    return jsonify(cursor_to_df(cursor).to_json())

@app.route('/predictive-relationship', methods=['POST'])
@cross_origin(supports_credentials=True)
def predictive_relationship():
    table_name = str(request.json['name'])
    column = str(request.json['column'])
    bdb = get_bdb()
    with bdb.savepoint():
        sql_execute(bdb, drop_dependence_probability_table(table_name))
        create = create_dependence_probability_table(table_name)
        execute(bdb, create)
        query = select_dependence_probabilities(table_name, column)
        cursor = execute(bdb, query)
        result = [row[0] for row in cursor]
    return jsonify(result)

@app.route("/predict", methods=['post'])
@cross_origin(supports_credentials=True)
def predict():
    app.log.info(get_last_query())
    table_name = str(request.json['name'])
    row = request.json['row']
    column = str(request.json['column'])
    bdb = get_bdb()
    with bdb.savepoint():
        query = infer_explicit_predict(table_name, column)
        cursor = execute(bdb, query, [10, row])
        result = [row[0] for row in cursor]
    return jsonify(result)

@app.route("/find-anomalies", methods=['post'])
@cross_origin(supports_credentials=True)
def find_anomalies():
    table_name = "satellites_full"
    target = str(request.json['target'])
    context = [str(x) for x in request.json['context']]
    bdb = get_bdb()
    with bdb.savepoint():
        query = find_anomalies_query(table_name, target, context)
        cursor = execute(bdb, query)
        result = [row[0] for row in cursor]
    return jsonify(result)

@app.route("/find-peers", methods=['post'])
@cross_origin(supports_credentials=True)
def find_peers():
    table_name = "satellites_full"
    target = str(request.json['target'])
    context = [str(x) for x in request.json['context']]
    bdb = get_bdb()
    with bdb.savepoint():
        query = find_peer_rows_query(table_name, target, context)
        cursor = execute(bdb, query)
        result = [[row[0], row[1]] for row in cursor]
    return jsonify(result)

def is_file(arg):
    """
    File 'type' for use with argparse. Raises an error of the argument is not
    the path to a valid file.

    """
    if not os.path.isfile(arg):
        raise argparse.ArgumentTypeError("{0} does not exist or is not a file".format(arg))
    else:
        return arg

def parse_log_level(s):
    valid_levels = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET']
    if s not in valid_levels:
        raise ValueError('Invalid log level: {}'.format(s))
    return getattr(logging, s, logging.NOTSET)

if __name__ == '__main__':
    app.config.from_pyfile('application_defaults.cfg')
    app.config.from_envvar('BAYESREST_SETTINGS')

    log_level = app.config['LOG_LEVEL']
    app.logger.info('setting log level to: {0}'.format(log_level))
    logging.getLogger(__name__).level = parse_log_level(log_level)


    flask_cors_log_level = app.config['FLASK_CORS_LOG_LEVEL']
    app.logger.info('setting flask_cors log level to: {0}'.format(flask_cors_log_level))
    logging.getLogger('flask_cors').level = parse_log_level(flask_cors_log_level)

    app.run(host='0.0.0.0', port=5000, debug=True)
