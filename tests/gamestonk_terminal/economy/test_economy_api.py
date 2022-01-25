# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY

# IMPORTATION INTERNAL
from gamestonk_terminal.helper_classes import ModelsNamespace as _models
from gamestonk_terminal.economy import economy_api


def test_models():
    assert isinstance(economy_api.models, _models)
