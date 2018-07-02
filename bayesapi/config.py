from aumbry import Attr, YamlConfig

class AppConfig(YamlConfig):
    __mapping__ = {
        'bdb_file': Attr('bdb_file', str),
        'table_name': Attr('table_name', str),
        'population_name': Attr('population_name', str),
        'log_level': Attr('log_level', str),
        'history': Attr('history', dict),
        'gunicorn': Attr('gunicorn', dict),
    }
