from openbb_terminal.forecast import theta_model
from tests.openbb_terminal.forecast import conftest


def test_get_theta_model(tsla_csv):
    conftest.test_model(theta_model.get_theta_data, tsla_csv)
