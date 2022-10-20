import pytest
from tests.openbb_terminal.forecast import conftest

try:
    from openbb_terminal.forecast import trans_model
except ImportError:
    pytest.skip(allow_module_level=True)


def test_get_trans_model(tsla_csv):
    conftest.test_model(trans_model.get_trans_data, tsla_csv, n_epochs=1)
