# IMPORTATION STANDARD
from types import ModuleType

# IMPORTATION THIRDPARTY

# IMPORTATION INTERNAL
from openbb_terminal.stocks.behavioural_analysis import ba_api


def test_module_loaded():
    assert isinstance(ba_api, ModuleType)
