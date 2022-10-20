import pytest
from tests.openbb_terminal.forecast import conftest

try:
    from openbb_terminal.forecast import nbeats_model
except ImportError:
    pytest.skip(allow_module_level=True)


def test_get_NBEATS_model(tsla_csv):
    conftest.test_model(nbeats_model.get_NBEATS_data, tsla_csv, n_epochs=1)
