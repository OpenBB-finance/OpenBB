import pytest
from tests.openbb_terminal.forecast import conftest

try:
    from openbb_terminal.forecast import nhits_model
except ImportError:
    pytest.skip(allow_module_level=True)


def test_get_nhits_model(tsla_csv):
    conftest.test_model(nhits_model.get_nhits_data, tsla_csv, n_epochs=1)


def test_get_nhits_model_past_covs(tsla_csv):
    conftest.test_model(
        nhits_model.get_nhits_data, tsla_csv, n_epochs=1, past_covariates="open"
    )
