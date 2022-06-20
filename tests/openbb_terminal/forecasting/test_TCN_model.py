from openbb_terminal.forecasting import tcn_model
from tests.openbb_terminal.forecasting import conftest


def test_get_TCN_model(recorder, tsla_csv):
    value = conftest.test_model(tcn_model.get_tcn_data, tsla_csv, n_epochs=1)

    recorder.capture(value)
