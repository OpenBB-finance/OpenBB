from openbb_terminal.forecasting import TCN_model
from tests.openbb_terminal.forecasting import conftest


def test_get_TCN_model(recorder, tsla_csv):
    value = conftest.test_model(TCN_model.get_tcn_data, tsla_csv, n_epochs=1)

    recorder.capture(value)
