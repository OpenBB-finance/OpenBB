from datetime import datetime, timedelta

import pandas as pd
import pytest

from openbb_terminal.stocks.tradinghours import bursa_model

TRADING_HOURS_DF = pd.read_csv(
    "tests/openbb_terminal/stocks/tradinghours/csv/test_bursa_model/trading_hours_df.csv",
    index_col=0,
)

DAYS_TILL_NEXT_MONDAY = (0 - datetime.utcnow().date().weekday()) % 7
NEXT_MONDAY = datetime.utcnow() + timedelta(days=DAYS_TILL_NEXT_MONDAY)
DAYS_TILL_NEXT_SUNDAY = (6 - datetime.utcnow().date().weekday()) % 7
NEXT_SUNDAY = datetime.utcnow() + timedelta(days=DAYS_TILL_NEXT_SUNDAY)


@pytest.mark.parametrize(
    "current_time, exchange, expected",
    [
        (NEXT_MONDAY.replace(hour=8, minute=0, second=0), "AAA", False),
        (NEXT_MONDAY.replace(hour=9, minute=0, second=0), "AAA", False),
        (NEXT_MONDAY.replace(hour=12, minute=30, second=0), "AAA", False),
        (NEXT_MONDAY.replace(hour=13, minute=15, second=0), "AAA", False),
        (NEXT_MONDAY.replace(hour=17, minute=45, second=0), "AAA", False),
        (NEXT_MONDAY.replace(hour=20, minute=0, second=0), "AAA", False),
        (NEXT_MONDAY.replace(hour=9, minute=30, second=0), "AAA", True),
        (NEXT_MONDAY.replace(hour=9, minute=45, second=0), "AAA", True),
        (NEXT_MONDAY.replace(hour=11, minute=0, second=0), "AAA", True),
        (NEXT_MONDAY.replace(hour=12, minute=10, second=0), "AAA", True),
        (NEXT_MONDAY.replace(hour=13, minute=45, second=0), "AAA", True),
        (NEXT_MONDAY.replace(hour=14, minute=0, second=0), "AAA", True),
        (NEXT_MONDAY.replace(hour=17, minute=0, second=0), "AAA", True),
        (NEXT_MONDAY.replace(hour=12, minute=30, second=0), "BBB", True),
        (NEXT_SUNDAY.replace(hour=14, minute=0, second=0), "AAA", False),
        (NEXT_SUNDAY.replace(hour=14, minute=0, second=0), "BBB", False),
    ],
)
def test_check_if_open(current_time, exchange, expected, mocker):
    path_model = "openbb_terminal.stocks.tradinghours.bursa_model"

    mocked_datetime = mocker.patch(target=f"{path_model}.datetime")

    mocked_datetime.utcnow().replace().astimezone.return_value = current_time
    mocked_datetime.strptime = datetime.strptime

    is_open = bursa_model.check_if_open(TRADING_HOURS_DF, exchange)

    assert is_open == expected
