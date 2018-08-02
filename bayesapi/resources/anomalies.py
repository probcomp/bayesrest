import falcon
import history
from bayesapi.resources import BaseResource
from bayesapi.validation import validate

class AnomaliesResource(BaseResource):

    def on_post(self, req, resp):

        req_vars = validate(self.api_def, 'post', req)

        target_column = req_vars['target-column']
        context_columns = req_vars['context-columns']

        quoted_tgt_column = '"{}"'.format(target_column)
        quoted_ctx_columns = ['"{}"'.format(c) for c in context_columns]

        with self.bdb.savepoint():
            query = self.queries.find_anomalies(
                population = self.cfg.population_name,
                target_column = quoted_tgt_column,
                context_columns = quoted_ctx_columns
            )

            self.logger.info(query)

            cursor = self.execute(query)
            cols = ['row-id','probability']
            result = [dict(zip(cols, row)) for row in cursor]

            history.save(self.cfg.history,
                         {'type': 'anomalies',
                          'query': query,
                          'result': result,
                          'target_column': target_column,
                          'context_columns': context_columns})

        resp.media = result
        resp.status = falcon.HTTP_200
