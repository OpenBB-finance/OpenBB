# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import numpy as np
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.technical_analysis import finnhub_view

PATTERN_DF = pd.DataFrame(
    data={
        0: {
            "aprice": 1.09236,
            "atime": 1641337200,
            "bprice": 1.1109,
            "btime": 1568322000,
            "cprice": 1.09897,
            "ctime": 1568667600,
            "dprice": 0.0,
            "dtime": 0,
            "end_price": 1.1109,
            "end_time": 1568926800.0,
            "entry": 1.1109,
            "eprice": 0.0,
            "etime": 0.0,
            "mature": 0,
            "patternname": "Double Bottom",
            "patterntype": "bullish",
            "profit1": 1.1294,
            "profit2": 0.0,
            "sortTime": 1568926800,
            "start_price": 1.1109,
            "start_time": 1566853200.0,
            "status": "incomplete",
            "stoploss": 1.0905,
            "symbol": "EUR_USD",
            "terminal": 0,
            "przmax": np.nan,
            "przmin": np.nan,
            "rrratio": np.nan,
            "xprice": np.nan,
            "xtime": np.nan,
        },
        1: {
            "aprice": 1.09236,
            "atime": 1641337200,
            "bprice": 1.1109,
            "btime": 1568322000,
            "cprice": 1.09897,
            "ctime": 1568667600,
            "dprice": 1.13394884,
            "dtime": 1568926800,
            "end_price": np.nan,
            "end_time": np.nan,
            "entry": 1.1339,
            "eprice": np.nan,
            "etime": np.nan,
            "mature": 0,
            "patternname": "Bat",
            "patterntype": "bearish",
            "profit1": 1.1181,
            "profit2": 1.1082,
            "sortTime": 1568667600,
            "start_price": np.nan,
            "start_time": np.nan,
            "status": "incomplete",
            "stoploss": 1.1416,
            "symbol": "EUR_USD",
            "terminal": 0,
            "przmax": 1.1339,
            "przmin": 1.129,
            "rrratio": 3.34,
            "xprice": 1.1393,
            "xtime": 1561669200.0,
        },
    }
)
DF_STOCK = pd.DataFrame(
    data={
        "Open": {
            pd.Timestamp("2022-01-04 00:00:00"): 95.7699966430664,
            pd.Timestamp("2022-01-05 00:00:00"): 96.0,
        },
        "High": {
            pd.Timestamp("2022-01-04 00:00:00"): 96.94000244140625,
            pd.Timestamp("2022-01-05 00:00:00"): 97.06999969482422,
        },
        "Low": {
            pd.Timestamp("2022-01-04 00:00:00"): 95.52999877929688,
            pd.Timestamp("2022-01-05 00:00:00"): 95.48999786376953,
        },
        "Close": {
            pd.Timestamp("2022-01-04 00:00:00"): 96.33999633789062,
            pd.Timestamp("2022-01-05 00:00:00"): 95.94999694824219,
        },
        "Adj Close": {
            pd.Timestamp("2022-01-04 00:00:00"): 96.33999633789062,
            pd.Timestamp("2022-01-05 00:00:00"): 95.94999694824219,
        },
        "Volume": {
            pd.Timestamp("2022-01-04 00:00:00"): 5372400,
            pd.Timestamp("2022-01-05 00:00:00"): 7180100,
        },
    }
)


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_query_parameters": [
            ("token", "MOCK_TOKEN"),
            ("period1", "MOCK_PERIOD_1"),
            ("period2", "MOCK_PERIOD_2"),
            ("date", "MOCK_DATE"),
        ]
    }


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_plot_pattern_recognition(mocker):
    # MOCK DOWNLOAD
    mocker.patch(
        target="gamestonk_terminal.stocks.technical_analysis.finnhub_view.yf.download",
        return_value=DF_STOCK,
    )

    # MOCK RESPONSE
    mocker.patch(
        target="gamestonk_terminal.stocks.technical_analysis.finnhub_model.get_pattern_recognition",
        return_value=PATTERN_DF,
    )

    # MOCK PLOT
    mocker.patch(
        target="gamestonk_terminal.stocks.technical_analysis.finnhub_view.mpf.plot"
    )

    # MOCK EXPORT_DATA
    mocker.patch(
        target="gamestonk_terminal.stocks.technical_analysis.finnhub_view.export_data"
    )

    finnhub_view.plot_pattern_recognition(
        ticker="PM",
        resolution="D",
        export="csv",
    )
