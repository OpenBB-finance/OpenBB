import pytest
from tests.openbb_terminal.forecast import conftest

try:
    from openbb_terminal.forecast import tft_model
except ImportError:
    pytest.skip(allow_module_level=True)


def test_get_tft_model(tsla_csv):
    conftest.test_model(tft_model.get_tft_data, tsla_csv, n_epochs=1)
