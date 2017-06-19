#import bayeslite

# https://docs.python.org/2/library/json.html

def random_name():
	return "some_name"

def serialize_value(val):
	if isinstance(val, str):
		return "\"%s\"" %(val)
	elif isinstance(val, int) or isinstance(val,float):
		return str(val)
	else:
		raise ValueError("%s is of type %s. Can only serialize ints and floats.") %(val, type(val))

def create_table(matrix):
	table_name = random_name()
	col_names = ', '.join(str(m) for m in matrix[0][:])
	values = ''
	for i, row in enumerate(matrix[1:][:]):
		cur_values = ', '.join([serialize_value(r) for r in row])
		cur_values = '(%s)' %(cur_values)
		values += cur_values
		if i != len(matrix) - 2:
			values +=','
	return "CREATE TABLE %s (%s) VALUES (%s)" %(table_name, col_names, values)

def create_population(table_name):
	population_name = random_name()
	return "CREATE POPULATION %s FOR %s WITH SCHEMA ( GUESS(*) )" %(table_name, population_name)

def create_metamodel(population_name):
	metamodel_name = random_name()
	return "CREATE METAMODEL %s FOR %s WITH BASELINE crosscat()" %(population_name, metamodel_name)

def initialize_models(metamodel_name, num_models=1):
	return "INITIALIZE %d MODELS FOR %s" %(num_models, metamodel_name)

def analyze_metamodel(metamodel_name, num_minutes=1):
	return "ANALYZE %s FOR %d MINUTES WAIT ( OPTIMIZED )" %(metamodel_name, num_minutes)
