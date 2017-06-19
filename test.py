import bayeslite
from bayesdb_flask import *

bdb = bayeslite.bayesdb_open('test.bdb')

matrix = [["Name", "Age"], ["Zane", 35], ["Vikash", 36]]

clear_artifacts_queries = clear_artifacts("some_name")
for caq in clear_artifacts_queries:
	print caq
	with bdb.savepoint():
		bdb.execute(caq)

create_table_query = create_table(matrix)
bdb.sql_execute(create_table_query)
insert_values_query = insert_values("some_name", matrix)
bdb.sql_execute(insert_values_query)

queries = [create_population("some_name"), create_metamodel("some_name_p"), \
           initialize_models("some_name_m"), analyze_metamodel("some_name_m")]

for query in queries:
    print query
    with bdb.savepoint():
        bdb.execute(query)
