from openbb_terminal.forecast import brnn_model
from tests.openbb_terminal.forecast import conftest


def test_get_brnn_model(tsla_csv):
    conftest.test_model(brnn_model.get_brnn_data, tsla_csv, n_epochs=1)


def test_get_brnn_model_past_covs(tsla_csv):
    conftest.test_model(
        brnn_model.get_brnn_data, tsla_csv, n_epochs=1, past_covariates="open"
    )
