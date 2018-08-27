import falcon
import history

from bayesapi.resources import BaseResource

class FIPSColumnResource(BaseResource):

    def on_get(self, req, resp):

        table_name = self.cfg.table_name
        fips_col_name = 'state_county_fips'

        with self.bdb.savepoint():

            def column_names():
                query = self.queries.get_full_table(table_name=table_name)
                cursor = self.execute(query)
                return {tuple[0] for tuple in cursor.description}

            if fips_col_name in column_names():
                resp.status = 200
                resp.media = { 'fips-column-name': fips_col_name }

            elif fips_col_name not in column_names():
                resp.status = 200
                resp.media = { 'fips-column-name': None }
