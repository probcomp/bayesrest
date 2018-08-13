import aumbry
from gunicorn.app.base import BaseApplication
import logging
import os
import yaml

from bayesapi.config import AppConfig

import bayeslite
from bayeslite.backends.cgpm_backend import CGPM_Backend
from bayeslite.backends.loom_backend import LoomBackend

class GunicornApp(BaseApplication):

    def __init__(self, cfg, bdb, api_def, logger):
        self.options = cfg.gunicorn or {}
        super(GunicornApp, self).__init__()

        self.app_cfg = cfg
        self.bdb = bdb
        self.api_def = api_def
        self.logger = logger

    def load_config(self):
        for key, value in self.options.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        # we do this here so live reloading works...
        # https://github.com/benoitc/gunicorn/issues/1237
        # https://github.com/benoitc/gunicorn/issues/1562
        from bayesapi.app import APIService
        from falcon_cors import CORS
        cors = CORS(allow_origins_list=["https://bayessheets.probcomp.dev:8443"],
                    allow_credentials_all_origins=True,
                    allow_all_headers=True,
                    allow_headers_list=["Content-Type"], allow_all_methods=True)

        self.application = APIService(self.app_cfg, self.bdb,
                                      self.api_def, self.logger,
                                      middleware=[cors.middleware])
        return self.application


def get_backend_object(cfg):
    if cfg.backend is None:
        raise RuntimeError('BACKEND was not set in config file')

    if cfg.backend == 'cgpm':
        return CGPM_Backend({}, multiprocess=False)
    elif cfg.backend == 'loom':
        return LoomBackend(cfg.loom_path)

def get_bdb(cfg, logger):
    logger.info("Using bdb file: {}".format(cfg.bdb_file))

    bdb = bayeslite.bayesdb_open(pathname=cfg.bdb_file)
    bayeslite.bayesdb_register_backend(bdb, get_backend_object(cfg))

    if cfg.backend == 'loom':
        # These are hacks that are necessary because bayeslite currently
        # assumes that `.bdb` file creation and querying will happen in the
        # same Python process.
        logger.info('Backend is set to {}. Manually setting loom_store_path to {}'.format(cfg.backend, cfg.loom_path))
        bdb.sql_execute('UPDATE bayesdb_loom_generator SET loom_store_path = ?', (cfg.loom_path,))
        logger.info('Backend is set to {}. Analyzing for 1 iterations.'.format(cfg.backend))
        bdb.execute('ANALYZE data FOR 1 ITERATIONS;')

    logger.info("Backend registered")

    return bdb

def parse_log_level(s):
    valid_levels = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET']
    if s not in valid_levels:
        raise ValueError('Invalid log level: {}'.format(s))
    return getattr(logging, s, logging.NOTSET)

def read_api(fn):
    with open('api.yaml') as api:
        api_def = yaml.load(api)

    return api_def

def main():
    logging.basicConfig()

    cfg = aumbry.load(aumbry.FILE, AppConfig)

    logging.getLogger(__name__).level = parse_log_level(cfg.log_level)
    logger = logging.getLogger(__name__)

    logger.info('Using bayeslite version: {}'.format(bayeslite.__version__))

    bdb = get_bdb(cfg, logger)

    api_def = read_api('api.yaml')

    gunicorn_app = GunicornApp(cfg, bdb, api_def, logger)

    gunicorn_app.run()

if __name__ == '__main__':
    main()
