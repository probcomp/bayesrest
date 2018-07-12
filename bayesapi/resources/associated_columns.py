import falcon
import history

from bayesapi.resources import BaseResource
from bayesapi.validation import validate

class AssociatedColumnsResource(BaseResource):
    def on_post(self, req, resp):
        table_name = self.cfg.table_name

        req_vars = validate(self.api_def, 'post', req)
        target_column = req_vars['column']

        def normalize(column):
            return column.lower()

        with self.bdb.savepoint():
            def column_names():
                query = self.queries.get_full_table(table_name=table_name)
                cursor = self.execute(query)
                return [tuple[0] for tuple in cursor.description]

            case_mapping = {normalize(column): column for column in column_names()}

        with self.bdb.savepoint():
            create_depprob_table_query = self.queries.create_dependence_probability_table(
                population = self.cfg.population_name
            )

            self.execute(create_depprob_table_query)

            query = self.queries.select_dependence_probabilities(column_name=normalize(target_column))
            result = self.execute(query)

            maps = [{'column': case_mapping[row[0]], 'score': row[1]}
                for row
                in result.fetchall()
                if case_mapping[row[0]] != target_column]

        maps.insert(0, {'column': target_column, 'score': 1.0})

        resp.media = maps
        resp.status = 200
