import falcon
import history

from bayesapi.resources import BaseResource
from bayesapi.validation import validate

class FIPSDataResource(BaseResource):
    def on_post(self, req, resp):

        table_name = self.cfg.table_name
        fips_col_name = 'state_county_fips'

        with self.bdb.savepoint():

            def column_names():
                query = self.queries.get_full_table(table_name=table_name)
                cursor = self.execute(query)
                return {tuple[0] for tuple in cursor.description}

            if fips_col_name not in column_names():
                resp.status = 400
                return

        with self.bdb.savepoint():

            q = self.queries.get_fips_data(table_name = table_name,
                                           fips_col_name = fips_col_name)
            cursor = self.execute(q)
            cols = ['row-id','fips-id']
            result = [dict(zip(cols, row)) for row in cursor]

        resp.media = result
        resp.status = 200
