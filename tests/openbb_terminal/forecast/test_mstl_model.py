import pytest
from tests.openbb_terminal.forecast import conftest

try:
    from openbb_terminal.forecast import mstl_model
except ImportError:
    pytest.skip(allow_module_level=True)


def test_get_mstl_model(tsla_csv):
    conftest.test_model(mstl_model.get_mstl_data, tsla_csv)
