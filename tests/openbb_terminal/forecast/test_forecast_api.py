import pytest
from openbb_terminal.helper_classes import ModelsNamespace

# pylint: enable=E1101
try:
    from openbb_terminal.forecast import forecast_api  # type: ignore
except ImportError:
    pytest.skip(allow_module_level=True)


def test_api():
    assert isinstance(forecast_api.models, ModelsNamespace)
