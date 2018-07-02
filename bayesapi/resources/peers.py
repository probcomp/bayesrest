import falcon
import history

from bayesapi.resources import BaseResource
from bayesapi.validation import validate

class PeersResource(BaseResource):

    def on_post(self, req, resp):

        req_vars = validate(self.api_def, 'post', req)

        target_row = req_vars['target-row']
        context_column = req_vars['context-column']

        with self.bdb.savepoint():
            query = self.queries.find_peer_rows(
                population = self.cfg.population_name,
                context_column = context_column,
                target_row = target_row
            )

            cursor = self.execute(query)
            result = [[row[0], row[1]] for row in cursor]

            history.save(self.cfg.history,
                         {'type': 'peers',
                          'query': query,
                          'result': result,
                          'target_row': target_row,
                          'context_columns': [context_column]})

        resp.media = result
        resp.status = falcon.HTTP_200
