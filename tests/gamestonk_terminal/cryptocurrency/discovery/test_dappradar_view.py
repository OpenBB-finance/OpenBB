# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.cryptocurrency.discovery import dappradar_view


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
    }


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "func, kwargs",
    [
        ("display_top_nfts", dict()),
        ("display_top_games", dict()),
        ("display_top_dexes", dict()),
        ("display_top_dapps", dict()),
    ],
)
def test_call_func(func, kwargs, mocker):
    # MOCK EXPORT_DATA
    mocker.patch(
        target="openbb_terminal.cryptocurrency.discovery.dappradar_view.export_data"
    )

    getattr(dappradar_view, func)(**kwargs)


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "func, kwargs, mocked_func",
    [
        (
            "display_top_nfts",
            dict(),
            "get_top_nfts",
        ),
        (
            "display_top_games",
            dict(),
            "get_top_games",
        ),
        (
            "display_top_dexes",
            dict(),
            "get_top_dexes",
        ),
        (
            "display_top_dapps",
            dict(),
            "get_top_dapps",
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
