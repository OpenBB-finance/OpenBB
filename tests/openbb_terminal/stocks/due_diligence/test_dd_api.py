# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY

# IMPORTATION INTERNAL
from openbb_terminal.helper_classes import ModelsNamespace as _models
from openbb_terminal.stocks.due_diligence import dd_api


def test_models():
    assert isinstance(dd_api.models, _models)
