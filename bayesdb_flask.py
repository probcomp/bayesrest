import bayeslite

# https://docs.python.org/2/library/json.html

def create_population_name(table_name):
	return table_name + "_p"

def create_metamodel_name(table_name):
	return table_name + "_m"

def serialize_value(val):
	val = str(val)
	if isinstance(val, str):
		return "\"%s\"" %(val)
	elif isinstance(val, int) or isinstance(val,float):
		return str(val)
	else:
		raise ValueError("%s is of type %s. Can only serialize ints and floats." %(str(val), str(type(val))))

def clear_artifacts(table_name):
	return ["DROP METAMODEL IF EXISTS %s" %(create_metamodel_name(table_name)), \
			"DROP POPULATION IF EXISTS %s" %(create_population_name(table_name)), \
			"DROP TABLE IF EXISTS %s" %(table_name)]

def create_bdb(table_name):
	return bayeslite.bayesdb_open(table_name + '.bdb')

def column_names(matrix):
	return ', '.join(serialize_value(m) for m in matrix[0][:])

def create_table(table_name, matrix):
	col_names = column_names(matrix)
	return "CREATE TABLE %s (%s)" %(table_name, col_names)

def insert_values(table_name, matrix):
    values = ''
    for i, row in enumerate(matrix[1:][:]):
		cur_values = ', '.join([serialize_value(r) for r in row])
		cur_values = '(%s)' %(cur_values)
		values += cur_values
		if i != len(matrix) - 2:
			values +=','
    col_names = column_names(matrix)
    return "INSERT INTO %s (%s) VALUES %s" %(table_name, col_names, values)

def create_population(table_name):
	return "CREATE POPULATION %s FOR %s WITH SCHEMA ( GUESS(*) )" %(create_population_name(table_name), table_name)

def create_metamodel(table_name):
	return "CREATE METAMODEL %s FOR %s WITH BASELINE crosscat()" % (create_metamodel_name(table_name), create_population_name(table_name))

def initialize_models(table_name, num_models=1):
	return "INITIALIZE %d MODELS FOR %s" %(num_models, create_metamodel_name(table_name))

def analyze_metamodel(table_name, num_minutes=1):
	return "ANALYZE %s FOR %d MINUTES WAIT ( OPTIMIZED )" %(create_metamodel_name(table_name), num_minutes)

def simulate(table_name, var_name, limit=10):
	return "SIMULATE %s FROM %s LIMIT %d" %(var_name, create_population_name(table_name), limit)
