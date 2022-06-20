from openbb_terminal.forecasting import linregr_model
from tests.openbb_terminal.forecasting import conftest


def test_get_linear_regression_model(recorder, tsla_csv):
    value = conftest.test_model(
        linregr_model.get_linear_regression_data, tsla_csv, random_state=1
    )

    recorder.capture(value)
