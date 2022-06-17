from openbb_terminal.forecasting import rnn_model
from tests.openbb_terminal.forecasting import conftest


def test_get_rnn_model(recorder, tsla_csv):
    value = conftest.test_model(rnn_model.get_rnn_data, tsla_csv, n_epochs=1)

    recorder.capture(value)
