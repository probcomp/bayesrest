import falcon

from bayesapi.resources import BaseResource
from bayesapi.validation import validate

class ColumnDataResource(BaseResource):

    def on_post(self, req, resp):

        req_vars = validate(self.api_def, 'post', req)

        table_name = self.cfg.table_name

        def fix_fips(k, v):
            if k == self.fips['state']:
                sv = str(v)
                return sv.zfill(2)
            elif k == self.fips['county']:
                sv = str(v)
                return sv.zfill(5)
            return v

        def fix_fips_if_present(result):
            return { k : fix_fips(k, v) for k, v in result.iteritems() }

        def normalize(column):
            return column.lower()

        columns = [c for c in req_vars['columns']]

        with self.bdb.savepoint():
            def column_name_set():
                query = self.queries.get_full_table(table_name=table_name)
                cursor = self.execute(query)
                return {normalize(tuple[0]) for tuple in cursor.description}

            for c in columns:
                if normalize(c) not in column_name_set():
                    resp.status = 400
                    return

        with self.bdb.savepoint():
            query = self.queries.column_data(
                column_names = ['"{}"'.format(c) for c in columns],
                table_name = '"{}"'.format(table_name)
            )

            cursor = self.execute(query)

            db_col_names = [k for k in columns]
            db_col_names.insert(0, 'row-id')

            results = [ dict(zip(db_col_names, row)) for row in cursor ]

            resp.media = [fix_fips_if_present(r) for r in results]
            resp.status = falcon.HTTP_200
