# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY

# IMPORTATION INTERNAL
from openbb_terminal.helper_classes import ModelsNamespace as _models
from openbb_terminal.stocks.options import options_api


def test_models():
    assert isinstance(options_api.models, _models)
