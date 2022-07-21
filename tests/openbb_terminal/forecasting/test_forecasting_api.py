from openbb_terminal.forecasting import forecasting_api
from openbb_terminal.helper_classes import ModelsNamespace


def test_api():
    assert isinstance(forecasting_api.models, ModelsNamespace)
