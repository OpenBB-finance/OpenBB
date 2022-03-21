# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest
import yfinance

# IMPORTATION INTERNAL
from gamestonk_terminal.economy import yfinance_view


@pytest.mark.vcr
@pytest.mark.parametrize(
    "indices, interval, start_date, end_date, column, store",
    [
        [["sp500", "nasdaq"], "1d", "2022-01-01", "2022-02-02", "Adj Close", False],
        [
            ["cac40", "dowjones", "nasdaq"],
            "1wk",
            "2020-06-06",
            "2020-07-07",
            "Close",
            False,
        ],
        [["dowjones"], "1mo", "2015-01-01", "2015-02-02", "Volume", False],
        [["cac40"], "3mo", "2010-01-01", "2016-02-06", "High", True],
    ],
)
def test_show_indices(mocker, indices, interval, start_date, end_date, column, store):
    yf_download = yfinance.download

    def mock_yf_download(*args, **kwargs):
        kwargs["threads"] = False
        return yf_download(*args, **kwargs)

    mocker.patch("yfinance.download", side_effect=mock_yf_download)
    mocker.patch(
        target="gamestonk_terminal.helper_classes.TerminalStyle.visualize_output"
    )
    result_df = yfinance_view.show_indices(
        indices, interval, start_date, end_date, column, store
    )

    assert isinstance(result_df, pd.DataFrame)


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "keyword, limit",
    [[["s&p", "500"], 5], [["world", "index"], 2], [["dow", "jones"], 10]],
)
def test_search_indices(keyword, limit):
    yfinance_view.search_indices(keyword, limit)
