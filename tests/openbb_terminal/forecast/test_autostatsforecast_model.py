import pytest
from tests.openbb_terminal.forecast import conftest

try:
    from openbb_terminal.forecast import autostatsforecast_model
except ImportError:
    pytest.skip(allow_module_level=True)


def test_get_autostatsforecast_model(tsla_csv):
    conftest.test_model(autostatsforecast_model.get_autostatsforecast_data, tsla_csv)
