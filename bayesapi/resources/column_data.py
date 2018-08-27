import falcon

from bayesapi.resources import BaseResource
from bayesapi.validation import validate

class ColumnDataResource(BaseResource):

    def on_post(self, req, resp):

        req_vars = validate(self.api_def, 'post', req)

        table_name = self.cfg.table_name

        columns = req_vars['columns']

        with self.bdb.savepoint():
            query = self.queries.column_data(
                column_names = ['"{}"'.format(c) for c in columns],
                table_name = '"{}"'.format(table_name)
            )

            cursor = self.execute(query)

            result = [ dict(zip(columns, row)) for row in cursor ]

            resp.media = result
            resp.status = falcon.HTTP_200
