# IMPORTATION STANDARD
from datetime import datetime

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.dark_pool_shorts import sec_model

all_ftds = pd.DataFrame(
    data={
        "SETTLEMENT DATE": [20211115, 20211115, 20211115, 20211115, 20211115],
        "CUSIP": ["B38564108", "C00948106", "C96657116", "D18190898", "F21107101"],
        "SYMBOL": ["EURN", "AGRI", "VMAR", "DB", "CSTM"],
        "QUANTITY (FAILS)": [41288, 18732, 376, 2875, 14642],
        "DESCRIPTION": [
            "EURONAV NV ANTWERPEN (BELGIUM)",
            "AGRIFORCE GROWING SYS LTD COM ",
            "VISION MARINE TECHNOLOGIES INC",
            "DEUTSCHE BANK AG NAMEN AKT (DE",
            "CONSTELLIUM SE CL A SHS USD (F",
        ],
        "PRICE": [10.24, 2.32, 6.59, 12.76, 19.63],
    }
)


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
    }


@pytest.mark.vcr
@pytest.mark.parametrize(
    "num",
    [1, 0],
)
def test_get_fails_to_deliver(mocker, num, recorder):
    mocker.patch(
        target="pandas.read_csv",
        new=mocker.Mock(return_value=all_ftds.copy()),
    )
    result_df = sec_model.get_fails_to_deliver(
        ticker="EURN",
        start=datetime.strptime("2021-12-01", "%Y-%m-%d"),
        end=datetime.strptime("2021-12-02", "%Y-%m-%d"),
        num=num,
    )

    recorder.capture(result_df)
