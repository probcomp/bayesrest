from aumbry import Attr, YamlConfig
from aumbry.contract import AumbryConfig
from alchemize.transmute import JsonTransmuter
from aumbry.formats.yml import YamlHandler
import os

class EnvYamlHandler(YamlHandler):

    def deserialize(self, raw_config, config_cls):
        import yaml

        config_dict = yaml.load(raw_config)
        for k in config_dict.keys():
            config_dict[k] = os.environ.get(k.upper()) or config_dict[k]

        return JsonTransmuter.transmute_from(config_dict, config_cls)


class EnvYamlConfig(AumbryConfig):
    __handler__ = EnvYamlHandler


class AppConfig(EnvYamlConfig):

    __mapping__ = {
        'bdb_file': Attr('bdb_file', str),
        'loom_path': Attr('loom_path', str),
        'table_name': Attr('table_name', str),
        'population_name': Attr('population_name', str),
        'backend': Attr('backend', str),
        'log_level': Attr('log_level', str),
        'history': Attr('history', dict),
        'gunicorn': Attr('gunicorn', dict),
    }
