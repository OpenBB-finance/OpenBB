from openbb_terminal.forecasting import regression_model
from tests.openbb_terminal.forecasting import conftest


def test_get_regression_model(recorder, tsla_csv):
    value = conftest.test_model(regression_model.get_regression_data, tsla_csv)

    recorder.capture(value)
