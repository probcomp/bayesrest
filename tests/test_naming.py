import bayeslite
from bayesdb_flask import *

def test_population_naming():
    assert create_population_name("test") == "test_p"
