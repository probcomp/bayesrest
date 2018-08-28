import falcon

from bayesapi.resources import BaseResource
from bayesapi.validation import validate

class ColumnDataResource(BaseResource):

    def on_post(self, req, resp):

        req_vars = validate(self.api_def, 'post', req)

        table_name = self.cfg.table_name

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

            result = [ dict(zip(db_col_names, row)) for row in cursor ]

            resp.media = result
            resp.status = falcon.HTTP_200
