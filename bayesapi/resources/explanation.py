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
