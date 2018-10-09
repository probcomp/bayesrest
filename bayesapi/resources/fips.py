import falcon
import history

from bayesapi.resources import BaseResource

class FIPSColumnResource(BaseResource):

    def on_get(self, req, resp):

        resp.status = 200
        resp.media = self.fips
