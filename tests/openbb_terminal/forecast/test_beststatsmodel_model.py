import pytest
from tests.openbb_terminal.forecast import conftest

try:
    from openbb_terminal.forecast import beststatsmodel_model
except ImportError:
    pytest.skip(allow_module_level=True)


def test_get_beststatsmodel_model(tsla_csv):
    conftest.test_model(beststatsmodel_model.get_beststatsmodel_data, tsla_csv)
