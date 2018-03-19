import bayeslite
from bayesdb_flask import *

bdb = bayeslite.bayesdb_open('test.bdb')

matrix = [["Name", "Age"], ["Zane", 35], ["Vikash", 36]]
table_name = "some_name"

clear_artifacts_queries = clear_artifacts("some_name")
for caq in clear_artifacts_queries:
	print caq
	with bdb.savepoint():
		bdb.execute(caq)

create_table_query = create_table(matrix)
bdb.sql_execute(create_table_query)
insert_values_query = insert_values(table_name, matrix)
bdb.sql_execute(insert_values_query)

queries = [create_population(table_name), create_metamodel(table_name), \
           initialize_models(table_name), analyze_metamodel(table_name)]

for query in queries:
    print query
    with bdb.savepoint():
        bdb.execute(query)
