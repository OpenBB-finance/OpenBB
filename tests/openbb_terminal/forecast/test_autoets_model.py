import pytest
from tests.openbb_terminal.forecast import conftest

try:
    from openbb_terminal.forecast import autoets_model
except ImportError:
    pytest.skip(allow_module_level=True)


def test_get_autoets_model(tsla_csv):
    conftest.test_model(autoets_model.get_autoets_data, tsla_csv)
