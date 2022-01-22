# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY

# IMPORTATION INTERNAL
from gamestonk_terminal.helper_classes import ModelsNamespace as _models
from gamestonk_terminal.stocks.discovery import disc_api


def test_models():
    assert isinstance(disc_api.models, _models)
