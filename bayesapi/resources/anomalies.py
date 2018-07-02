import falcon

from bayesapi.resources import BaseResource
from bayesapi.validation import validate

class AnomaliesResource(BaseResource):

    def on_post(self, req, resp):

        req_vars = validate(self.api_def, 'post', req)

        target_column = req_vars['target-column']
        context_columns = req_vars['context-columns']

        with self.bdb.savepoint():
            query = self.queries.find_anomalies(
                conditions=[self.queries.cond_anomalies_context],
                population = self.cfg.population_name,
                target_column=target_column,
                context_columns=context_columns
            )

            cursor = self.execute(query)
            full_result = [row for row in cursor]
            # client_result = [r for r in full_result]

        resp.media = full_result
        resp.status = falcon.HTTP_200
