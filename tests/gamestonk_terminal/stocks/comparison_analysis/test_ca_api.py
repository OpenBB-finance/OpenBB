# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY

# IMPORTATION INTERNAL
from gamestonk_terminal.helper_classes import ModelsNamespace as _models
from gamestonk_terminal.stocks.comparison_analysis import ca_api


def test_models():
    assert isinstance(ca_api.models, _models)
