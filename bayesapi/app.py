import falcon

# from example.db.manager import DBManager
# from example.middleware.context import ContextMiddleware

from bayesapi.resource_map import resources

class APIService(falcon.API):
    def __init__(self, cfg, bdb, api_def, fips, logger, **kwargs):
        self.logger = logger
        super(APIService, self).__init__(**kwargs)

        self.bdb = bdb
        self.cfg = cfg

        for r in resources:
            res = r['resource_class']
            path = r['path']
            api = api_def['paths'][path]
            instance = res(cfg, self.bdb, api, fips, logger)
            self.add_route(r['path'], instance)

    def start(self):
        """ A hook to when a Gunicorn worker calls run()."""
        pass

    def stop(self, signal):
        """ A hook to when a Gunicorn worker starts shutting down. """
        pass
