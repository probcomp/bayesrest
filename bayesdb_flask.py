import bayeslite

# https://docs.python.org/2/library/json.html

def random_name():
	return "some_name"

def create_population_name(table_name):
	return table_name + "_p"

def create_metamodel_name(table_name):
	return table_name + "_m"

def serialize_value(val):
	if isinstance(val, str):
		return "\"%s\"" %(val)
	elif isinstance(val, int) or isinstance(val,float):
		return str(val)
	else:
		raise ValueError("%s is of type %s. Can only serialize ints and floats.") %(val, type(val))

def clear_artifacts(table_name):
	return ["DROP METAMODEL IF EXISTS %s" %(create_metamodel_name(table_name)), \
			"DROP POPULATION IF EXISTS %s" %(create_population_name(table_name)), \
			"DROP TABLE IF EXISTS %s" %(table_name)]

def create_table(matrix):
	table_name = random_name()
	col_names = ', '.join(str(m) for m in matrix[0][:])
	return "CREATE TABLE %s (%s)" %(table_name, col_names)

def insert_values(table_name, matrix):
    values = ''
    for i, row in enumerate(matrix[1:][:]):
		cur_values = ', '.join([serialize_value(r) for r in row])
		cur_values = '(%s)' %(cur_values)
		values += cur_values
		if i != len(matrix) - 2:
			values +=','
    col_names = ', '.join(str(m) for m in matrix[0][:])
    return "INSERT INTO %s (%s) VALUES %s" %(table_name, col_names, values)

def create_population(table_name):
	return "CREATE POPULATION %s FOR %s WITH SCHEMA ( GUESS(*) )" %(create_population_name(table_name), table_name)

def create_metamodel(table_name):
	return "CREATE METAMODEL %s FOR %s WITH BASELINE crosscat()" % (create_metamodel_name(table_name), create_population_name(table_name))

def initialize_models(table_name, num_models=1):
	return "INITIALIZE %d MODELS FOR %s" %(num_models, create_metamodel_name(table_name))

def analyze_metamodel(table_name, num_minutes=1):
	return "ANALYZE %s FOR %d MINUTES WAIT ( OPTIMIZED )" %(create_metamodel_name(table_name), num_minutes)

