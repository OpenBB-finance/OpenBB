# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pandas as pd

# IMPORTATION INTERNAL
from openbb_terminal.stocks.dark_pool_shorts import nyse_model


df = pd.DataFrame(
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
        "Short Exempt Volume": [
            2570,
            2402,
            3450,
            958,
            5007,
            1450,
            1359,
            420,
            706,
            2082,
        ],
        "Short Volume": [
            299274,
            157886,
            250632,
            359399,
            668542,
            268801,
            200122,
            141903,
            183300,
            238361,
        ],
        "Total Volume": [
            373525,
            203060,
            317996,
            418209,
            825620,
            360326,
            268511,
            206546,
            243163,
            362592,
        ],
    }
)


def test_get_short_data_by_exchange(mocker, recorder):
    mock_find_one = mocker.Mock(find_one=mocker.Mock(return_value=df))
    NYSE_ShortData = {
        "ARCA": mock_find_one,
        "Amex": mock_find_one,
        "Chicago": mock_find_one,
        "National": mock_find_one,
        "NYSE": mock_find_one,
    }
    mock_client = mocker.MagicMock(NYSE_ShortData=NYSE_ShortData)
    mocker.patch(
        target="pymongo.MongoClient",
        new=mock_client,
    )
    result_df = nyse_model.get_short_data_by_exchange(
        ticker="TSLA",
    )

    recorder.capture(result_df)
