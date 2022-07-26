from openbb_terminal.forecast import regr_model
from tests.openbb_terminal.forecast import conftest


def test_get_regression_model(tsla_csv):
    conftest.test_model(regr_model.get_regression_data, tsla_csv)
