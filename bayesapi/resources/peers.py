import falcon
import history

from bayesapi.resources import BaseResource
from bayesapi.validation import validate

class PeersResource(BaseResource):

    def on_post(self, req, resp):

        req_vars = validate(self.api_def, 'post', req)

        target_row = req_vars['target-row']
        context_column = req_vars['context-column']

        quoted_ctx_column = '"{}"'.format(context_column)

        with self.bdb.savepoint():
            query = self.queries.find_peer_rows(
                population = self.cfg.population_name,
                context_column = quoted_ctx_column,
                target_row = target_row
            )

            cursor = self.execute(query)
            cols = ['row-id','similarity']
            result = [dict(zip(cols, row)) for row in cursor]

            history.save(self.cfg.history,
                         {'type': 'peers',
                          'query': query,
                          'result': result,
                          'target_row': target_row,
                          'context_columns': [context_column]})

            history.save(self.cfg.history,
                         { 'result': result },
                         "similarity")


        resp.media = result
        resp.status = falcon.HTTP_200
