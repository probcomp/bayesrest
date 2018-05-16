import argparse
import json
import logging
import os

import flask
from flask import Flask, request, send_file
from flask.json import jsonify
from flask_cors import CORS, cross_origin
from snaql.factory import Snaql
import pickle

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

def get_table_name():
    if not 'TABLE_NAME' in app.config:
        raise RuntimeError('TABLE_NAME was not set in config file')
    return app.config['TABLE_NAME']

def get_population_name():
    if not 'POPULATION_NAME' in app.config:
        raise RuntimeError('POPULATION_NAME was not set in config file')
    return app.config['POPULATION_NAME']

def save_explanation_data(data):
    pickle.dump(data, open("/tmp/bayes-query", "wb"))

def get_explanation_data():
    res = pickle.load(open("/tmp/bayes-query", "rb"))
    return res

def pairwise_similarity_of_rows(table_name, context_column, row_ids):
    bdb = get_bdb()

    with bdb.savepoint():
        query = queries.pairwise_similarity(
            population=get_population_name(),
            context_column=context_column,
            row_set=row_ids
        )

        cursor = execute(bdb, query)
        result = [[row[0], row[1], row[2]] for row in cursor]

    return result

def sql_execute(bdb, query, *args):
    app.logger.info('sql executing query: %s', query)
    return bdb.sql_execute(query, *args)

def execute(bdb, query, *args):
    app.logger.info('executing query: %s', query)
    return bdb.execute(query, *args)

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
    last_data = get_explanation_data()
    return jsonify({'last_query': last_data['query'],
                    'type': last_data['type'],
                    'target_column': last_data.get('target_column'),
                    'context_columns': last_data.get('context_columns')})

@app.route('/peer-heatmap-data', methods=['GET'])
@cross_origin(supports_credentials=True)
def heatmap_data():
    table_name = get_table_name()
    last_data = get_explanation_data()
    context_column = last_data['context_columns'][0] # only one supported for now

    top_results = last_data['result'][:100]
    top_row_ids = ",".join([str(row [0]) for row in top_results])

    bottom_results = last_data['result'][-100:]
    bottom_row_ids = ",".join([str(row [0]) for row in bottom_results])

    result = [pairwise_similarity_of_rows(table_name, context_column, top_row_ids),
              pairwise_similarity_of_rows(table_name, context_column, bottom_row_ids)]

    return jsonify(result)

@app.route('/anomaly-scatterplot-data', methods=['GET'])
@cross_origin(supports_credentials=True)
def anomaly_data():
    last_data = get_explanation_data()
    result = last_data['result']
    return jsonify(result)

@app.route('/table-data', methods=['GET'])
@cross_origin(supports_credentials=True)
def table_data():
    table_name = get_table_name()
    query = queries.get_full_table(
        table_name=table_name
    )

    bdb = get_bdb()
    cursor = execute(bdb, query)
    col_name_list = [tuple[0] for tuple in cursor.description]

    return jsonify({'columns': col_name_list,
                    'data': [r for r in cursor] })

@app.route("/find-anomalies", methods=['post'])
@cross_origin(supports_credentials=True)
def find_anomalies():
    table_name = get_table_name()
    target_column = str(request.json['target-column'])
    context_columns = request.json['context-columns']
    bdb = get_bdb()
    with bdb.savepoint():
        query = queries.find_anomalies(
            conditions=[queries.cond_anomalies_context],
            population=get_population_name(),
            target_column=target_column,
            context_columns=context_columns
        )
        cursor = execute(bdb, query)
        full_result = [row for row in cursor]
        client_result = [r for r in full_result]
        save_explanation_data({'type': 'anomalies',
                               'query': query,
                               'result': full_result,
                               'target_column': target_column,
                               'context_columns': context_columns})
    return jsonify(client_result)

@app.route("/find-peers", methods=['post'])
@cross_origin(supports_credentials=True)
def find_peers():
    table_name = get_table_name()
    target_row = str(request.json['target-row'])
    context_column = request.json['context-column']
    bdb = get_bdb()
    with bdb.savepoint():
        query = queries.find_peer_rows(
            population=get_population_name(),
            context_column=context_column,
            target_row=target_row
        )
        cursor = execute(bdb, query)
        result = [[row[0], row[1]] for row in cursor]
        save_explanation_data({'type': 'peers',
                               'query': query,
                               'result': result,
                               'target_row': target_row,
                               'context_columns': [context_column]})
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
