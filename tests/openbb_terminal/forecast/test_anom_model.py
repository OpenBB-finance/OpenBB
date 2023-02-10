import pytest

from tests.openbb_terminal.forecast import conftest

try:
    from openbb_terminal.forecast import anom_model
except ImportError:
    pytest.skip(allow_module_level=True)


def test_get_anom_model(tsla_csv):
    conftest.test_anom_model(anom_model.get_anomaly_detection_data, tsla_csv)
