# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY

# IMPORTATION INTERNAL
from gamestonk_terminal.helper_classes import ModelsNamespace as _models
from gamestonk_terminal.cryptocurrency.discovery import discovery_api


def test_models():
    assert isinstance(discovery_api.models, _models)
