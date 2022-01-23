# IMPORTATION STANDARD
from datetime import datetime
from io import BytesIO

# IMPORTATION THIRDPARTY
import numpy as np
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.comparison_analysis import yahoo_finance_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("period1", "1598220000"),
            ("period2", "1635980400"),
        ],
    }


@pytest.mark.skip
@pytest.mark.vcr
def test_get_historical(mocker, recorder):
    # FORCE SINGLE THREADING
    yf_download = yahoo_finance_model.yf.download

    def mock_yf_download(*args, **kwargs):
        kwargs["threads"] = False
        return yf_download(*args, **kwargs)

    mocker.patch("yfinance.download", side_effect=mock_yf_download)

    result_df = yahoo_finance_model.get_historical(
        similar_tickers=["TSLA", "GM"],
        start=datetime.strptime("2020-12-21", "%Y-%m-%d"),
        candle_type="o",
    )

    recorder.capture(result_df)


def filter_reduce_csv(response):
    """To reduce cassette size."""

    headers = response["headers"]
    if (
        "Expect-CT" in headers
        and isinstance(headers["Expect-CT"], list)
        and len(headers["Expect-CT"]) > 0
        and "yahoo" in headers["Expect-CT"][0]
    ):
        return response

    content = response["body"]["string"]
    df = pd.read_csv(filepath_or_buffer=BytesIO(content), index_col=0)
    if len(df) > 10:
        response["body"]["string"] = df.head(10).to_csv().encode()
    return response


@pytest.mark.skip
@pytest.mark.vcr(before_record_response=filter_reduce_csv)
def test_get_sp500_comps_tsne(mocker, recorder):
    # FORCE SINGLE THREADING
    yf_download = yahoo_finance_model.yf.download

    def mock_yf_download(*args, **kwargs):
        kwargs["threads"] = False
        return yf_download(*args, **kwargs)

    mocker.patch("yfinance.download", side_effect=mock_yf_download)

    mocker.patch(
        "gamestonk_terminal.stocks.comparison_analysis.yahoo_finance_model.normalize",
        side_effect=lambda x: x,
    )
    mocker.patch("matplotlib.pyplot.show")
    mocker.patch(
        "sklearn.manifold.TSNE.fit_transform",
        side_effect=lambda x: np.full((len(x), 2), 1),
    )
    result_df = yahoo_finance_model.get_sp500_comps_tsne(
        ticker="TOT.TO",
    )

    recorder.capture(result_df)
