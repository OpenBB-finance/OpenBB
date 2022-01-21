# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.screener import finviz_view
from gamestonk_terminal import helper_funcs


@pytest.mark.vcr
@pytest.mark.parametrize(
    "toggle",
    [
        True,
        False,
    ],
)
@pytest.mark.record_stdout
def test_screener(mocker, toggle):
    # MOCK CHARTS
    mocker.patch.object(
        target=helper_funcs.gtff,
        attribute="USE_TABULATE_DF",
        new=toggle,
    )

    # MOCK EXPORT_DATA
    mocker.patch(
        target="gamestonk_terminal.stocks.screener.finviz_view.export_data",
    )

    # MOCK PROGRESS_BAR
    mocker.patch(
        target="finvizfinance.screener.overview.progressBar",
    )

    finviz_view.screener(
        loaded_preset="top_gainers",
        data_type="overview",
        limit=2,
        ascend=True,
        sort=["Ticker"],
        export="",
    )


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "data",
    [
        None,
        pd.DataFrame(),
    ],
)
def test_screener_no_data(data, mocker):
    # MOCK GET_SCREENER_DATA
    mocker.patch(
        target="gamestonk_terminal.stocks.screener.finviz_view.get_screener_data",
        return_value=data,
    )

    result = finviz_view.screener(
        loaded_preset="top_gainers",
        data_type="overview",
        limit=2,
        ascend=True,
        sort="",
        export="",
    )

    assert result == []  # pylint: disable=use-implicit-booleaness-not-comparison


@pytest.mark.vcr
@pytest.mark.parametrize(
    "sort",
    [
        ["Ticke"],
        ["MOCK_SORT"],
    ],
)
@pytest.mark.record_stdout
def test_screener_sort_matches(sort, mocker):
    # MOCK CHARTS
    mocker.patch.object(
        target=helper_funcs.gtff,
        attribute="USE_TABULATE_DF",
        new=True,
    )

    # MOCK EXPORT_DATA
    mocker.patch(
        target="gamestonk_terminal.stocks.screener.finviz_view.export_data",
    )

    # MOCK PROGRESS_BAR
    mocker.patch(
        target="finvizfinance.screener.overview.progressBar",
    )

    finviz_view.screener(
        loaded_preset="top_gainers",
        data_type="overview",
        limit=2,
        ascend=True,
        sort=sort,
        export="",
    )
