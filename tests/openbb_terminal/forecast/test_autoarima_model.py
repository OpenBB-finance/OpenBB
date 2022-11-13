import pytest
from tests.openbb_terminal.forecast import conftest

try:
    from openbb_terminal.forecast import autoarima_model
except ImportError:
    pytest.skip(allow_module_level=True)


def test_get_autoarima_model(tsla_csv):
    conftest.test_model(autoarima_model.get_autoarima_data, tsla_csv)
