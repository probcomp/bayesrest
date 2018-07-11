import aumbry
from gunicorn.app.base import BaseApplication
import logging
import os
import yaml

from bayesapi.config import AppConfig

import bayeslite
from bayeslite.backends.cgpm_backend import CGPM_Backend

class GunicornApp(BaseApplication):

    def __init__(self, cfg, bdb, api_def):
        self.options = cfg.gunicorn or {}
        self.app_cfg = cfg
        self.bdb = bdb
        self.api_def = api_def
        super(GunicornApp, self).__init__()

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
                                      self.api_def, middleware=[cors.middleware])
        return self.application

def get_bdb(cfg, logger):

    bdb = bayeslite.bayesdb_open(pathname=cfg.bdb_file, builtin_backends=False)
    cgpm_backend = CGPM_Backend({}, multiprocess=False)
    bayeslite.bayesdb_register_backend(bdb, cgpm_backend)
    logger.info(cfg.bdb_file)

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

    cfg = aumbry.load(
        aumbry.FILE,
        AppConfig,
        {
            'CONFIG_FILE_PATH': './config.yaml'
        }
    )

    logging.getLogger(__name__).level = parse_log_level(cfg.log_level)
    logger = logging.getLogger(__name__)

    bdb = get_bdb(cfg, logger)

    api_def = read_api('api.yaml')

    gunicorn_app = GunicornApp(cfg, bdb, api_def)

    gunicorn_app.run()

if __name__ == '__main__':
    main()
