# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.dark_pool_shorts import nyse_view


df_get_short_data_by_exchange = pd.DataFrame(
    data={
        "Date": [
            pd.Timestamp("2021-01-04 00:00:00"),
            pd.Timestamp("2021-01-05 00:00:00"),
            pd.Timestamp("2021-01-06 00:00:00"),
            pd.Timestamp("2021-01-07 00:00:00"),
            pd.Timestamp("2021-01-08 00:00:00"),
            pd.Timestamp("2021-01-11 00:00:00"),
            pd.Timestamp("2021-01-12 00:00:00"),
            pd.Timestamp("2021-01-13 00:00:00"),
            pd.Timestamp("2021-01-14 00:00:00"),
            pd.Timestamp("2021-01-15 00:00:00"),
        ],
        "ShortExempt": [
            25601,
            11220,
            21133,
            13006,
            24509,
            11902,
            11231,
            6880,
            4658,
            6279,
        ],
        "ShortVolume": [
            2664870,
            1618500,
            2165234,
            2973925,
            4522989,
            2214677,
            1554661,
            1184689,
            1097063,
            1103615,
        ],
        "TotalVolume": [
            3421677,
            2109930,
            2876587,
            3719545,
            5750053,
            2975285,
            2131163,
            1671770,
            1532743,
            1907601,
        ],
        "Exchange": [
            "ARCA",
            "ARCA",
            "ARCA",
            "ARCA",
            "ARCA",
            "ARCA",
            "ARCA",
            "ARCA",
            "ARCA",
            "ARCA",
        ],
        "NetShort": [
            2690471,
            1629720,
            2186367,
            2986931,
            4547498,
            2226579,
            1565892,
            1191569,
            1101721,
            1109894,
        ],
        "PctShort": [
            0.786301863092279,
            0.7724047717222846,
            0.7600559273889509,
            0.8030366617422292,
            0.790861927707449,
            0.7483582245062238,
            0.7347593778608206,
            0.7127589321497575,
            0.7187904299677115,
            0.581827122128789,
        ],
    }
)


@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "toggle",
    [True, False],
)
def test_display_short_by_exchange(mocker, toggle):
    mocker.patch.object(target=nyse_view, attribute="USE_ION", new=False)
    mocker.patch("matplotlib.pyplot.show")
    mocker.patch("plotly.basedatatypes.BaseFigure.show")
    mocker.patch(
        target="gamestonk_terminal.stocks.dark_pool_shorts.nyse_model.get_short_data_by_exchange",
        new=mocker.Mock(return_value=df_get_short_data_by_exchange.copy()),
    )
    nyse_view.display_short_by_exchange(
        ticker="TSLA",
        raw=toggle,
        sort="",
        asc=toggle,
        mpl=toggle,
        export="",
    )
