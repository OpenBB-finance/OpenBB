import pytest
from openbb_terminal.helper_classes import ModelsNamespace

try:
    from openbb_terminal.forecast import forecast_api
except ImportError:
    pytest.skip(allow_module_level=True)


def test_api():
    assert isinstance(forecast_api.models, ModelsNamespace)
