# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY

# IMPORTATION INTERNAL
from gamestonk_terminal.helper_classes import ModelsNamespace as _models
from gamestonk_terminal.stocks.prediction_techniques import pred_api


def test_models():
    assert isinstance(pred_api.models, _models)
