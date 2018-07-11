import falcon
import history

from bayesapi.resources import BaseResource
from bayesapi.validation import validate

class AssociatedColumnsResource(BaseResource):

    def on_post(self, req, resp):

        req_vars = validate(self.api_def, 'post', req)
        target_column = req_vars['column']

        with self.bdb.savepoint():
            create_depprob_table_query = self.queries.create_dependence_probability_table(
                population = self.cfg.population_name
            )

            self.execute(create_depprob_table_query)

            query = self.queries.select_dependence_probabilities(column_name=target_column.lower())
            result = self.execute(query)

            order = [row[0] for row in result.fetchall()]

        # target column always comes first
        if target_column in order:
            order.remove(target_column)
        order.insert(0, target_column)

        resp.media = order
        resp.status = 200
