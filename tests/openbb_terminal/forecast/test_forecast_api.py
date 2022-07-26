from openbb_terminal.forecast import forecast_api
from openbb_terminal.helper_classes import ModelsNamespace


def test_api():
    assert isinstance(forecast_api.models, ModelsNamespace)
