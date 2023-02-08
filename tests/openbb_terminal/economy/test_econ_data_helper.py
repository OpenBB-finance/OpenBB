# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL


STOCK_DF = pd.DataFrame(
    data={
        "Open": {
            pd.Timestamp("2022-01-20 00:00:00"): 101.05999755859375,
            pd.Timestamp("2022-01-21 00:00:00"): 102.63999938964844,
        },
        "High": {
            pd.Timestamp("2022-01-20 00:00:00"): 102.77999877929688,
            pd.Timestamp("2022-01-21 00:00:00"): 103.75,
        },
        "Low": {
            pd.Timestamp("2022-01-20 00:00:00"): 100.68000030517578,
            pd.Timestamp("2022-01-21 00:00:00"): 102.33000183105469,
        },
        "Close": {
            pd.Timestamp("2022-01-20 00:00:00"): 102.0199966430664,
            pd.Timestamp("2022-01-21 00:00:00"): 102.91999816894531,
        },
        "Adj Close": {
            pd.Timestamp("2022-01-20 00:00:00"): 102.0199966430664,
            pd.Timestamp("2022-01-21 00:00:00"): 102.91999816894531,
        },
        "Volume": {
            pd.Timestamp("2022-01-20 00:00:00"): 5589700,
            pd.Timestamp("2022-01-21 00:00:00"): 5423100,
        },
        "date_id": {
            pd.Timestamp("2022-01-20 00:00:00"): 1,
            pd.Timestamp("2022-01-21 00:00:00"): 2,
        },
        "OC_High": {
            pd.Timestamp("2022-01-20 00:00:00"): 102.0199966430664,
            pd.Timestamp("2022-01-21 00:00:00"): 102.91999816894531,
        },
        "OC_Low": {
            pd.Timestamp("2022-01-20 00:00:00"): 101.05999755859375,
            pd.Timestamp("2022-01-21 00:00:00"): 102.63999938964844,
        },
        "OC_High_trend": {
            pd.Timestamp("2022-01-20 00:00:00"): 102.0199966430664,
            pd.Timestamp("2022-01-21 00:00:00"): 102.91999816894531,
        },
        "OC_Low_trend": {
            pd.Timestamp("2022-01-20 00:00:00"): 101.05999755859375,
            pd.Timestamp("2022-01-21 00:00:00"): 102.63999938964844,
        },
    }
)


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("period1", "MOCK_PERIOD_1"),
            ("period2", "MOCK_PERIOD_2"),
            ("date", "MOCK_DATE"),
        ],
    }
