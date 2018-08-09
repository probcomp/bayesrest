import falcon
import history

from bayesapi.resources import BaseResource
from bayesapi.validation import validate


class LastQueryResource(BaseResource):
    def on_get(self, req, resp):
        last_data = history.read(self.cfg.history)
        res = { 'last_query': last_data['query'],
                'type': last_data['type'],
                'target_column': last_data.get('target_column'),
                'context_columns': last_data.get('context_columns')}

        resp.media = res
        resp.status = 200

class AnomalyScatterplotDataResource(BaseResource):

    def on_get(self, req, resp):

        last_data = history.read(self.cfg.history)
        res = last_data['result']

        resp.media = res
        resp.status = 200

class PeerHeatmapDataResource(BaseResource):

    def pairwise_similarity_of_rows(self, table_name, context_column, row_ids):

        quoted_ctx_column = '"{}"'.format(context_column)

        with self.bdb.savepoint():
            query = self.queries.pairwise_similarity(
                population = self.cfg.population_name,
                context_column = quoted_ctx_column,
                row_set = row_ids
            )

            cursor = self.execute(query)
            result = [[row[0], row[1], row[2]] for row in cursor]

        return result

    def on_get(self, req, resp):
        table_name = self.cfg.table_name
        last_data = history.read(self.cfg.history)
        context_column = last_data['context_columns'][0] # only one supported for now

        top_results = last_data['result'][:100]
        top_row_ids = ",".join([str(row ['row-id']) for row in top_results])

        bottom_results = last_data['result'][-100:]
        bottom_row_ids = ",".join([str(row ['row-id']) for row in bottom_results])

        res = [self.pairwise_similarity_of_rows(table_name,
                                                context_column, top_row_ids),
               self.pairwise_similarity_of_rows(table_name,
                                                context_column, bottom_row_ids)]

        resp.media = res
        resp.status = 200
