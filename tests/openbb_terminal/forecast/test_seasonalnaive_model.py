import pytest
from tests.openbb_terminal.forecast import conftest

try:
    from openbb_terminal.forecast import seasonalnaive_model
except ImportError:
    pytest.skip(allow_module_level=True)


def test_get_seasonalnaive_model(tsla_csv):
    conftest.test_model(seasonalnaive_model.get_seasonalnaive_data, tsla_csv)
