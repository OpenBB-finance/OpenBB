from openbb_terminal.forecasting import theta_model
from tests.openbb_terminal.forecasting import conftest


def test_get_theta_model(recorder, tsla_csv):
    value = conftest.test_model(theta_model.get_theta_data, tsla_csv)

    recorder.capture(value)
