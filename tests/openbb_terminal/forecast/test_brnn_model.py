import pytest
from tests.openbb_terminal.forecast import conftest

try:
    from openbb_terminal.forecast import brnn_model
except ImportError:
    pytest.skip(allow_module_level=True)


def test_get_brnn_model(tsla_csv):
    conftest.test_model(brnn_model.get_brnn_data, tsla_csv, n_epochs=1)


def test_get_brnn_model_past_covs(tsla_csv):
    conftest.test_model(
        brnn_model.get_brnn_data, tsla_csv, n_epochs=1, past_covariates="open"
    )
