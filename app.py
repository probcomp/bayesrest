import argparse
import json
import logging
import os

import flask
from flask import Flask, request
from flask.json import jsonify
from flask_cors import CORS, cross_origin
from snaql.factory import Snaql

import bayeslite
from bayeslite import bayesdb_nullify
from bayeslite.backends.cgpm_backend import CGPM_Backend
from iventure import utils_bql

root_location = os.path.abspath(os.path.dirname(__file__))
snaql_factory = Snaql(root_location, 'queries')
queries = snaql_factory.load_queries('queries.sql')

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

def set_last_query(bdb, query):
    quoted_query = json.dumps(query)
    with bdb.savepoint():
        bdb.sql_execute(queries.create_last_query_table())
        bdb.sql_execute(queries.set_last_query(), [quoted_query])

def get_last_query(bdb):
    with bdb.savepoint():
        bdb.sql_execute(queries.create_last_query_table())
        cursor = bdb.sql_execute(queries.get_last_query())
    return json.loads(cursor.fetchone()[0])

def sql_execute(bdb, query, *args):
    app.logger.info('sql executing query: %s', query)
    return bdb.sql_execute(query, *args)

def execute(bdb, query, *args):
    set_last_query(bdb, query)
    app.logger.info('executing query: %s', query)
    return bdb.execute(query, *args)

def create_population_name(table_name):
    return table_name + '_p'

def create_generator_name(table_name):
    return table_name + '_crosscat'

def create_dependence_probability_name(table_name):
    return table_name + '_depprob'

@app.route('/heartbeat', methods=['GET'])
@cross_origin(supports_credentials=True)
def heartbeat():
    bdb = get_bdb()
    settings = ['BDB_FILE', 'LOG_LEVEL']
    return jsonify({key: app.config[key] for key in settings})

@app.route('/last-query', methods=['GET'])
@cross_origin(supports_credentials=True)
def last_query():
    bdb = get_bdb()
    return jsonify({'last_query': get_last_query(bdb)})

@app.route("/find-anomalies", methods=['post'])
@cross_origin(supports_credentials=True)
def find_anomalies():
    table_name = "satellites_full"
    target = str(request.json['target'])
    context = request.json['context']
    bdb = get_bdb()
    with bdb.savepoint():
        query = queries.find_anomalies(
            conditions=[queries.cond_anomalies_context],
            population=create_population_name(table_name),
            target_column=target,
            context_columns=context
        )
        cursor = execute(bdb, query)
        result = [row[0] for row in cursor]
    return jsonify(result)

@app.route("/find-peers", methods=['post'])
@cross_origin(supports_credentials=True)
def find_peers():
    table_name = "satellites_full"
    target = str(request.json['target'])
    context = request.json['context']
    bdb = get_bdb()
    with bdb.savepoint():
        query = queries.find_peer_rows(
            population=create_population_name(table_name),
            context_columns=context,
            target_row=target
        )
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
    logging.getLogger(__name__).level = parse_log_level(log_level)


    flask_cors_log_level = app.config['FLASK_CORS_LOG_LEVEL']
    logging.getLogger('flask_cors').level = parse_log_level(flask_cors_log_level)

    app.run(host='0.0.0.0', port=5000, debug=True)
