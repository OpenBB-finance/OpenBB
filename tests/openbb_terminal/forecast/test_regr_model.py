import pytest
from tests.openbb_terminal.forecast import conftest

try:
    from openbb_terminal.forecast import regr_model
except ImportError:
    pytest.skip(allow_module_level=True)


def test_get_regression_model(tsla_csv):
    conftest.test_model(regr_model.get_regression_data, tsla_csv)
