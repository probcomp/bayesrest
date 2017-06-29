from flask import Flask, request
from flask_cors import CORS, cross_origin
import bayeslite
from iventure.utils_bql import cursor_to_df
from bayesdb_flask import *
from OpenSSL import SSL

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
app.debug = True

@app.route("/analyze", methods=['POST']) 
@cross_origin(supports_credentials=True)
def analyze():
    print request.json
    table_name = str(request.json['name'])
    data = request.json['data']
    bdb = create_bdb(table_name)
    clear_artifacts_queries = clear_artifacts(table_name)
    with bdb.savepoint():
        for caq in clear_artifacts_queries:
            print caq
            bdb.execute(caq)
    sql_queries = [create_table(table_name, data), insert_values(table_name, data)]
    bql_queries = [create_population(table_name), create_metamodel(table_name),\
                initialize_models(table_name), analyze_metamodel(table_name)]
    for sq in sql_queries:
        with bdb.savepoint():
            print sq
            bdb.sql_execute(sq)
    for bq in bql_queries:
        with bdb.savepoint():
            print bq
            bdb.execute(bq)
    return "OK!"

@app.route("/query", methods=['GET'])
def query():
    table_name = "test"
    query = simulate(table_name, "Age")
    bdb = create_bdb(table_name)
    with bdb.savepoint():
        cursor = bdb.execute(query)
    return cursor_to_df(cursor).to_json()

if __name__ == "__main__":
    context = ('selfsigned.crt', 'selfsigned.key')
    app.run(host='localhost', port=5000, debug=True, ssl_context=context)

# openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout ~/selfsigned.key -out ~/selfsigned.crt
