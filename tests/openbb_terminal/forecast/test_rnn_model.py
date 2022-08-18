import pytest
from openbb_terminal.forecast import rnn_model
from tests.openbb_terminal.forecast import conftest


@pytest.mark.prediction
def test_get_rnn_model(tsla_csv):
    conftest.test_model(rnn_model.get_rnn_data, tsla_csv, n_epochs=1)
