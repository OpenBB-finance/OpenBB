# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.cryptocurrency.discovery import pycoingecko_view


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "func, kwargs",
    [
        ("display_coins", dict(category="analytics")),
        ("display_gainers", dict()),
        ("display_losers", dict()),
        ("display_trending", dict()),
    ],
)
def test_call_func(func, kwargs, mocker):
    # MOCK EXPORT_DATA
    mocker.patch(
        target="gamestonk_terminal.cryptocurrency.discovery.pycoingecko_view.export_data"
    )

    getattr(pycoingecko_view, func)(**kwargs)


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "func, kwargs, mocked_func",
    [
        (
            "display_coins",
            dict(category="analytics"),
            "get_coins",
        ),
        (
            "display_gainers",
            dict(),
            "get_gainers_or_losers",
        ),
        (
            "display_losers",
            dict(),
            "get_gainers_or_losers",
        ),
        (
            "display_trending",
            dict(),
            "get_trending_coins",
        ),
    ],
)
def test_call_func_empty_df(func, kwargs, mocked_func, mocker):
    view_path = "gamestonk_terminal.cryptocurrency.discovery.pycoingecko_view"

    # MOCK MOCKED_FUNC
    attrs = {"empty": True}
    mock_empty_df = mocker.Mock(**attrs)
    mocker.patch(
        target=f"{view_path}.pycoingecko_model.{mocked_func}",
        return_value=mock_empty_df,
    )

    getattr(pycoingecko_view, func)(**kwargs)
