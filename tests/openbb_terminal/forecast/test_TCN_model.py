from openbb_terminal.forecast import tcn_model
from tests.openbb_terminal.forecast import conftest


def test_get_TCN_model(tsla_csv):
    conftest.test_model(tcn_model.get_tcn_data, tsla_csv, n_epochs=1)
