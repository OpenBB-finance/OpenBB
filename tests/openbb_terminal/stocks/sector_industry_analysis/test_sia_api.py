# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY

# IMPORTATION INTERNAL
from openbb_terminal.helper_classes import ModelsNamespace as _models
from openbb_terminal.stocks.sector_industry_analysis import sia_api


def test_models():
    assert isinstance(sia_api.models, _models)
