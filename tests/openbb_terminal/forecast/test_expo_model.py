import pytest
from tests.openbb_terminal.forecast import conftest

try:
    from openbb_terminal.forecast import expo_model
except ImportError:
    pytest.skip(allow_module_level=True)


def test_get_expo_model(tsla_csv):
    conftest.test_model(expo_model.get_expo_data, tsla_csv)
