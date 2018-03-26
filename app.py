import json

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

@app.route('/analyze', methods=['POST'])
@cross_origin(supports_credentials=True)
def analyze():
    table_name = str(request.json['name'])
    data = request.json['data']
    bdb = create_bdb(table_name)
    bdb.backends['cgpm'].set_multiprocess(True)

    with bdb.savepoint():
        for query in clear_artifacts(table_name):
            print query[:100]
            bdb.execute(query)
        create_table_query = create_table(table_name, data)
        print create_table_query
        bdb.sql_execute(create_table_query)

        # insert rows
        columns = column_names(data)
        columns_str = ','.join([serialize_value(column) for column in columns])
        values_str = ','.join(['?' for column in columns])
        insert_query = 'INSERT INTO "%s" (%s) VALUES (%s)' % (
            table_name, columns_str, values_str)
        print insert_query
        for row in data[1:][:]:
            # TODO: SQL injection abound here
            print insert_query
            bdb.sql_execute(insert_query, row)

        # nullify
        bayesdb_nullify(bdb, table_name, '')

        for query in [create_population(table_name), \
                create_generator(table_name)]:
            print query[:100]
            bdb.execute(query)
        # originally ran 32 models
        for query in [initialize_models(table_name, 8), \
                analyze_generator(table_name, 10)]:
            print query[:100]
            bdb.execute(query)
    return 'OK'

@app.route('/query', methods=['GET'])
@cross_origin(supports_credentials=True)
def query():
    table_name = 'test'
    query = simulate(table_name, 'Age')
    bdb = create_bdb(table_name)
    with bdb.savepoint():
        cursor = bdb.execute(query)
    return cursor_to_df(cursor).to_json()

@app.route('/predictive-relationship', methods=['POST'])
@cross_origin(supports_credentials=True)
def predictive_relationship():
    table_name = str(request.json['name'])
    column = str(request.json['column'])
    print "column = ", column
    bdb = create_bdb(table_name) # should really be a shared filename
    print "TEST A"
    with bdb.savepoint():
        print "TEST B"
        bdb.sql_execute(drop_dependence_probability_table(table_name))
        print "TEST C"
        create = create_dependence_probability_table(table_name)
        print "create =", create
        bdb.execute(create)
        print "TEST D"
        query = select_dependence_probabilities(table_name, column)
        print query
        cursor = bdb.execute(query)
        result = [row[0] for row in cursor]
    print "TEST E"
    print json.dumps(result)
    print "TEST F"
    return json.dumps(result)

@app.route("/predict", methods=['post'])
@cross_origin(supports_credentials=True)
def predict():
    table_name = str(request.json['name'])
    row = request.json['row']
    column = str(request.json['column'])
    bdb = create_bdb(table_name)
    with bdb.savepoint():
        query = infer_explicit_predict(table_name, column)
        print query
        cursor = bdb.execute(query, [10, row])
        result = [row[0] for row in cursor]
    return json.dumps(result)

@app.route("/find-anomalies", methods=['post'])
@cross_origin(supports_credentials=True)
def find_anomalies():
    table_name = str(request.json['name'])
    target = str(request.json['target'])
    context = [str(x) for x in request.json['context']]
    bdb = create_bdb(table_name)
    with bdb.savepoint():
        query = find_anomalies_query(table_name, target, context)
        print query
        cursor = bdb.execute(query)
        result = [row[0] for row in cursor]
    return json.dumps(result)

@app.route("/find-peers", methods=['post'])
@cross_origin(supports_credentials=True)
def find_peers():
    table_name = "satellites_full"
    target = str(request.json['target'])
    context = [str(x) for x in request.json['context']]
    bdb = create_bdb(table_name)
    with bdb.savepoint():
        query = find_peer_rows_query(table_name, target, context)
        print query
        cursor = bdb.execute(query)
        result = [[row[0], row[1]] for row in cursor]
        print result
    return json.dumps(result)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
