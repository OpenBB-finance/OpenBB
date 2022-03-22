# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY

# IMPORTATION INTERNAL
from gamestonk_terminal.helper_classes import ModelsNamespace as _models
from gamestonk_terminal.forex import forex_api


def test_models():
    assert isinstance(forex_api.oanda.models, _models)
    assert isinstance(forex_api.ta.models, _models)
