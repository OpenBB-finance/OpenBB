from openbb_terminal.forecast import expo_model
from tests.openbb_terminal.forecast import conftest


def test_get_expo_model(tsla_csv):
    conftest.test_model(expo_model.get_expo_data, tsla_csv)
