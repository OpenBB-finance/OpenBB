# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY

# IMPORTATION INTERNAL
from gamestonk_terminal.helper_classes import ModelsNamespace as _models
from gamestonk_terminal.stocks.backtesting import bt_api


def test_models():
    assert isinstance(bt_api.models, _models)
