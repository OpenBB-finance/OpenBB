import datetime

import pytest

from openbb_terminal.routine_functions import match_and_return_openbb_keyword_date

TEST_TIME = datetime.datetime(2023, 5, 24, 17, 5, 55)

@pytest.fixture
def patch_now(monkeypatch):
    class mydatetime:
        @classmethod
        def now(cls):
            return TEST_TIME

    monkeypatch.setattr("datetime.datetime", mydatetime)

def test_days_ago(patch_now):
    assert match_and_return_openbb_keyword_date("$1DAYSAGO") == "2023-05-23"
    assert match_and_return_openbb_keyword_date("$10DAYSAGO") == "2023-05-14"
    assert match_and_return_openbb_keyword_date("$-5DAYSAGO") == ""

def test_months_ago(patch_now):
    assert match_and_return_openbb_keyword_date("$1MONTHSAGO") == "2023-04-24"
    assert match_and_return_openbb_keyword_date("$10MONTHSAGO") == "2022-07-24"
    assert match_and_return_openbb_keyword_date("$-5MONTHSAGO") == ""

def test_years_ago(patch_now):
    assert match_and_return_openbb_keyword_date("$1YEARSAGO") == "2022-05-24"
    assert match_and_return_openbb_keyword_date("$10YEARSAGO") == "2013-05-24"
    assert match_and_return_openbb_keyword_date("$-5YEARSAGO") == ""
