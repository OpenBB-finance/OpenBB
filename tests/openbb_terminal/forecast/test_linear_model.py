from openbb_terminal.forecast import linregr_model
from tests.openbb_terminal.forecast import conftest


def test_get_linear_regression_model(tsla_csv):
    conftest.test_model(
        linregr_model.get_linear_regression_data, tsla_csv, random_state=1
    )
