import json

from flask import Flask, request
from flask_cors import CORS, cross_origin
from OpenSSL import SSL

import bayeslite

from iventure.utils_bql import cursor_to_df

from bayesdb_flask import *

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
app.debug = True

@app.route("/analyze", methods=['POST'])
@cross_origin(supports_credentials=True)
def analyze():
    table_name = str(request.json['name'])
    data = request.json['data']
    bdb = create_bdb(table_name)
    bdb.metamodels['cgpm'].set_multiprocess(True)

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
        insert_query = "INSERT INTO \"%s\" (%s) VALUES (%s)" %(table_name, columns_str, values_str)
        print insert_query
        for row in data[1:][:]:
            # TODO: SQL injection abound here
            print insert_query
            bdb.sql_execute(insert_query, row)

        for query in [create_population(table_name), create_metamodel(table_name)]:
            print query[:100]
            bdb.execute(query)
        for query in [initialize_models(table_name, 32), analyze_metamodel(table_name)]:
            print query[:100]
            bdb.execute(query)
    return "OK"

@app.route("/query", methods=['GET'])
@cross_origin(supports_credentials=True)
def query():
    table_name = "test"
    query = simulate(table_name, "Age")
    bdb = create_bdb(table_name)
    with bdb.savepoint():
        cursor = bdb.execute(query)
    return cursor_to_df(cursor).to_json()

@app.route("/predictive-relationship", methods=['POST'])
@cross_origin(supports_credentials=True)
def predictive_relationship():
    table_name = str(request.json['name'])
    column = str(request.json['column'])
    bdb = create_bdb(table_name) # should really be a shared filename
    with bdb.savepoint():
        bdb.sql_execute(drop_dependence_probability_table(table_name))
        bdb.execute(create_dependence_probability_table(table_name))
        query = select_dependence_probabilities(table_name, column)
        print query
        cursor = bdb.execute(query)
        result = [row[0] for row in cursor]
    return json.dumps(result)

if __name__ == "__main__":
    context = ('selfsigned.crt', 'selfsigned.key')
    app.run(host='localhost', port=5000, debug=True, ssl_context=context)
