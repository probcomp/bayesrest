import json
import logging
from wsgiref import simple_server

import falcon

import requests

from config import AppConfig
import aumbry

import bayeslite
from bayeslite import bayesdb_nullify
from bayeslite.backends.cgpm_backend import CGPM_Backend
from iventure import utils_bql

class Peers(object):

    def __init__(self, db, config):
        self.db = db
        self.logger = logging.getLogger('bayesapi.' + __name__)

    def on_post(self, req, resp):
        self.logger.debug("I HAVE NO IDEA")
        target = req.media.get('target-row')
        context = req.media.get('context-column')

        resp.media = {'target': target}
        resp.status = falcon.HTTP_200

### OpenAPI, but not used yet
with open('api.json') as j:
    schema = json.load(j)

### config
options = {
    'CONFIG_FILE_PATH': './config.yaml',
}

# load config
config = aumbry.load(aumbry.FILE, AppConfig, options)

app = falcon.API()
peers = Peers(None, config)

app.add_route('/find-peers', peers)
# app.add_route('/find-anomalies', find-peers)


def open_bdb(config, logger):

    logger.info('instantiating a new bdb')
    bdb = bayeslite.bayesdb_open(pathname=config['BDB_FILE'], builtin_backends=False)
    cgpm_backend = CGPM_Backend({}, multiprocess=False)
    bayeslite.bayesdb_register_backend(bdb, cgpm_backend)
    return bdb


def parse_log_level(s):
    valid_levels = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET']
    if s not in valid_levels:
        raise ValueError('Invalid log level: {}'.format(s))
    return getattr(logging, s, logging.NOTSET)

if __name__ == '__main__':

    log_level = config.log_level
    logging.basicConfig()

    logging.getLogger(__name__).level = parse_log_level(log_level)
    logger = logging.getLogger(__name__)

    logger.debug("About to make server.")
    httpd = simple_server.make_server('0.0.0.0', 5000, app)
    logger.debug("WHWHWHWH!!!!!!")
    httpd.serve_forever()
