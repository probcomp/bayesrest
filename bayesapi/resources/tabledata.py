import falcon
from bayesapi.resources import BaseResource

class TableDataResource(BaseResource):

    def on_get(self, req, resp):
        table_name = self.cfg.table_name

        quoted_table_name = '"{}"'.format(table_name)

        query = self.queries.get_full_table(
            table_name = quoted_table_name
        )

        cursor = self.execute(query)
        col_name_list = [tuple[0] for tuple in cursor.description]
        res = { 'columns': col_name_list,
                'data': [r for r in cursor] }

        resp.media = res
        resp.status = 200
