# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY

# IMPORTATION INTERNAL
from gamestonk_terminal.helper_classes import ModelsNamespace as _models
from gamestonk_terminal.cryptocurrency.defi import defi_api


def test_models():
    assert isinstance(defi_api.models, _models)
