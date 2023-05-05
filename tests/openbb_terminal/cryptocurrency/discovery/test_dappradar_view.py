# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.cryptocurrency.discovery import dappradar_view


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [
            ("User-Agent", None),
            ("X-BLOBR-KEY", "MOCK_API_KEY"),
        ],
    }


@pytest.mark.record_http
@pytest.mark.record_verify_screen
@pytest.mark.parametrize(
    "func, kwargs",
    [
        ("display_nft_marketplaces", dict()),
        ("display_nft_marketplace_chains", dict()),
        ("display_dapps", dict()),
        ("display_dapp_categories", dict()),
        ("display_dapp_chains", dict()),
        ("display_token_chains", dict()),
        ("display_defi_chains", dict()),
    ],
)
def test_call_func(func, kwargs, mocker):
    # MOCK EXPORT_DATA
    mocker.patch(
        target="openbb_terminal.cryptocurrency.discovery.dappradar_view.export_data"
    )

    getattr(dappradar_view, func)(**kwargs)


@pytest.mark.record_verify_screen
@pytest.mark.parametrize(
    "func, kwargs, mocked_func",
    [
        (
            "display_nft_marketplaces",
            dict(),
            "get_nft_marketplaces",
        ),
        (
            "display_nft_marketplace_chains",
            dict(),
            "get_nft_marketplace_chains",
        ),
        (
            "display_dapps",
            dict(),
            "get_dapps",
        ),
        (
            "display_dapp_categories",
            dict(),
            "get_dapp_categories",
        ),
        (
            "display_dapp_chains",
            dict(),
            "get_dapp_chains",
        ),
        (
            "display_token_chains",
            dict(),
            "get_token_chains",
        ),
        (
            "display_defi_chains",
            dict(),
            "get_defi_chains",
        ),
    ],
)
def test_call_func_empty_df(func, kwargs, mocked_func, mocker):
    view_path = "openbb_terminal.cryptocurrency.discovery.dappradar_view"

    # MOCK MOCKED_FUNC
    attrs = {"empty": True}
    mock_empty_df = mocker.Mock(**attrs)
    mocker.patch(
        target=f"{view_path}.dappradar_model.{mocked_func}",
        return_value=mock_empty_df,
    )

    getattr(dappradar_view, func)(**kwargs)
