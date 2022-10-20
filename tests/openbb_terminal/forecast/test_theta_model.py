import pytest
from tests.openbb_terminal.forecast import conftest

try:
    from openbb_terminal.forecast import theta_model
except ImportError:
    pytest.skip(allow_module_level=True)


def test_get_theta_model(tsla_csv):
    conftest.test_model(theta_model.get_theta_data, tsla_csv)
