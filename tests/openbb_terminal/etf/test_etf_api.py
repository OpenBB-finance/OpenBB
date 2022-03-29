# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY

# IMPORTATION INTERNAL
from openbb_terminal.helper_classes import ModelsNamespace as _models
from openbb_terminal.etf import etf_api


def test_models():
    assert isinstance(etf_api.models, _models)
