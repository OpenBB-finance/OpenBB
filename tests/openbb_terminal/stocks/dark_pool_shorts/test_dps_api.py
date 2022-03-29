# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY

# IMPORTATION INTERNAL
from openbb_terminal.helper_classes import ModelsNamespace as _models
from openbb_terminal.stocks.dark_pool_shorts import dps_api


def test_models():
    assert isinstance(dps_api.models, _models)
