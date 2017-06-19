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

print create_table([["Name", "Age"], ["Zane", 35], ["Vikash", 36]])