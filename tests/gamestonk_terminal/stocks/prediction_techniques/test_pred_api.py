# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.helper_classes import ModelsNamespace as _models

try:
    from gamestonk_terminal.stocks.prediction_techniques import pred_api
except ImportError:
    pytest.skip(allow_module_level=True)


def test_models():
    assert isinstance(pred_api.models, _models)
