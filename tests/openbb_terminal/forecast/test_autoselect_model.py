import pytest
from tests.openbb_terminal.forecast import conftest

try:
    from openbb_terminal.forecast import autoselect_model
except ImportError:
    pytest.skip(allow_module_level=True)


def test_get_autoselect_model(tsla_csv):
    conftest.test_model(autoselect_model.get_autoselect_data, tsla_csv)
