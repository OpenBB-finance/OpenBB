import pytest
from tests.openbb_terminal.forecast import conftest

try:
    from openbb_terminal.forecast import linregr_model
except ImportError:
    pytest.skip(allow_module_level=True)


def test_get_linear_regression_model(tsla_csv):
    conftest.test_model(
        linregr_model.get_linear_regression_data, tsla_csv, random_state=1
    )
