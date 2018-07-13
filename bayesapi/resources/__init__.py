import os
from snaql.factory import Snaql

class BaseResource(object):
    def __init__(self, cfg, bdb, api_def, logger):
        self.bdb = bdb
        self.cfg = cfg
        self.api_def = api_def
        self.logger = logger

        root_location = os.path.abspath(os.path.dirname(__file__))
        snaql_factory = Snaql(root_location, 'queries')
        self.queries = snaql_factory.load_queries('queries.sql')

    def sql_execute(self, query, *args):
        return self.bdb.sql_execute(query, *args)

    def execute(self, query, *args):
        return self.bdb.execute(query, *args)
