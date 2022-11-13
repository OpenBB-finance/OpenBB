import pytest
from tests.openbb_terminal.forecast import conftest

try:
    from openbb_terminal.forecast import rwd_model
except ImportError:
    pytest.skip(allow_module_level=True)


def test_get_rwd_model(tsla_csv):
    conftest.test_model(rwd_model.get_rwd_data, tsla_csv)
