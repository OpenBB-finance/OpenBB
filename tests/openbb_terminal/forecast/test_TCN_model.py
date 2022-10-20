import pytest
from tests.openbb_terminal.forecast import conftest

try:
    from openbb_terminal.forecast import tcn_model
except ImportError:
    pytest.skip(allow_module_level=True)


def test_get_TCN_model(tsla_csv):
    conftest.test_model(tcn_model.get_tcn_data, tsla_csv, n_epochs=1)
