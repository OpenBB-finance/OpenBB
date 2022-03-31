# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY

# IMPORTATION INTERNAL
from gamestonk_terminal.helper_classes import ModelsNamespace as _models
from gamestonk_terminal.stocks.sector_industry_analysis import sia_api


def test_models():
    assert isinstance(sia_api.models, _models)
