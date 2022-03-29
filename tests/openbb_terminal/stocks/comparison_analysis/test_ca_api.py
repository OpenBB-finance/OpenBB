# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY

# IMPORTATION INTERNAL
from openbb_terminal.helper_classes import ModelsNamespace as _models
from openbb_terminal.stocks.comparison_analysis import ca_api


def test_models():
    assert isinstance(ca_api.models, _models)
