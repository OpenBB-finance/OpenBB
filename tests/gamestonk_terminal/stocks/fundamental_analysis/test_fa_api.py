# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY

# IMPORTATION INTERNAL
from openbb_terminal.helper_classes import ModelsNamespace as _models
from openbb_terminal.stocks.fundamental_analysis import fa_api


def test_models():
    assert isinstance(fa_api.models, _models)
