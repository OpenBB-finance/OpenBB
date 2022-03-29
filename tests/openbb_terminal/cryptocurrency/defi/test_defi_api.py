# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY

# IMPORTATION INTERNAL
from openbb_terminal.helper_classes import ModelsNamespace as _models
from openbb_terminal.cryptocurrency.defi import defi_api


def test_models():
    assert isinstance(defi_api.models, _models)
