# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY

# IMPORTATION INTERNAL
from gamestonk_terminal.helper_classes import ModelsNamespace as _models
from gamestonk_terminal.etf import etf_api


def test_models():
    assert isinstance(etf_api.models, _models)
