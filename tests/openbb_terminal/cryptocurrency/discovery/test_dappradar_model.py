# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.cryptocurrency.discovery import dappradar_model

# pylint: disable=protected-access


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None), ("X-BLOBR-KEY", "MOCK_API_KEY")],
    }


@pytest.mark.record_http
@pytest.mark.parametrize(
    "func, kwargs",
    [
        ("get_nft_marketplaces", dict()),
        ("get_nft_marketplace_chains", dict()),
        ("get_dapps", dict()),
        ("get_dapp_chains", dict()),
        ("get_dapp_categories", dict()),
        ("get_token_chains", dict()),
        ("get_defi_chains", dict()),
    ],
)
def test_call_func(func, kwargs, record):
    result = getattr(dappradar_model, func)(**kwargs)

    record.add_verify(result)
