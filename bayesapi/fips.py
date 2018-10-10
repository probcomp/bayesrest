import csv
import os
from snaql.factory import Snaql


def read_fips(fn):

    with open(fn) as fips_file:
        reader = csv.reader(fips_file, delimiter=',')
        cols = ['state-name', 'state-code', 'county-code','county-name','class-code']
        return [ dict(zip(cols, row)) for row in reader ]

def fips_sets(rows):

    states = set()
    counties = set()

    for row in rows:
        states.add(row['state-code'])
        counties.add("{}{}".format(row['state-code'], row['county-code']))

    return { 'states': states,
             'counties': counties }

# In order to be considered a "fips column", a column must contain at
# least 10% of either state or state-county fips values, and 90%
# column values must be either valid state or state-county values
def fips_cols(sets, col_names, cursor):

    state_count = len(sets['states'])
    county_count = len(sets['counties'])

    col_threshold = 0.10
    miss_threshold = 0.90

    scoreboard_init = [ {'name': c, 'county': 0, 'state': 0, 'miss': 0 } for c in col_names ]

    def keep_score(acc, r):
        for c, sb_row in zip(r, acc):
            cs = str(c)
            if cs.zfill(2) in sets['states']:
                sb_row['state'] += 1
            elif cs.zfill(5) in sets['counties']:
                sb_row['county'] += 1
            else:
                sb_row['miss'] += 1
        return acc

    scoreboard = reduce(keep_score, cursor, scoreboard_init)

    def resolve(acc, t):
        state_val = float(t['state']) / max(1, (t['state'] + t['miss']))
        county_val = float(t['county']) / max(1, (t['county'] + t['miss']))

        if state_val > miss_threshold \
           and state_val > acc['state']['val'] \
           and t['state'] / max(1, float(state_count)) > col_threshold:
            acc['state']['name'] = t['name']
            acc['state']['val'] = state_val

        if county_val > miss_threshold \
           and county_val > acc['county']['val'] \
           and t['county'] / max(1, float(county_count)) > col_threshold:
            acc['county']['name'] = t['name']
            acc['county']['val'] = state_val

        return acc

    resolved = reduce(resolve, scoreboard, {'state': {'name': None, 'val': 0},
                                            'county': {'name': None, 'val': 0}})

    ret = {'state': resolved['state']['name'],
           'county': resolved['county']['name']}

    return ret

def find_fips_cols(cfg, bdb, fips_file):

    root_location = os.path.abspath(os.path.dirname(__file__))
    snaql_factory = Snaql(root_location, 'resources/queries')
    queries = snaql_factory.load_queries('queries.sql')
    query = queries.get_full_table(table_name = '"{}"'.format(cfg.table_name))
    cursor = bdb.execute(query)

    sets = fips_sets(read_fips(fips_file))

    col_name_list = [tuple[0] for tuple in cursor.description]

    return fips_cols(sets, col_name_list, cursor)
