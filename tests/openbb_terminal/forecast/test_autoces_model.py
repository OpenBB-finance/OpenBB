import pytest
from tests.openbb_terminal.forecast import conftest

try:
    from openbb_terminal.forecast import autoces_model
except ImportError:
    pytest.skip(allow_module_level=True)


def test_get_autoces_model(tsla_csv):
    conftest.test_model(autoces_model.get_autoces_data, tsla_csv)
