from openbb_terminal.forecasting import trans_model
from tests.openbb_terminal.forecasting import conftest


def test_get_trans_model(tsla_csv):
    conftest.test_model(trans_model.get_trans_data, tsla_csv, n_epochs=1)
