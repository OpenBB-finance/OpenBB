# IMPORTATION STANDARD

import datetime
from pathlib import Path

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.core.session.current_user import (
    PreferencesModel,
    copy_user,
)
from openbb_terminal.helper_funcs import (
    check_start_less_than_end,
    export_data,
    remove_timezone_from_dataframe,
    revert_lambda_long_number_format,
    update_news_from_tweet_to_be_displayed,
)

# pylint: disable=E1101
# pylint: disable=W0603
# pylint: disable=E1111
# pylint: disable=W0621
# pylint: disable=W0613
# pylint: disable=R0912


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [
            ("User-Agent", None),
            ("Authorization", "MOCK_AUTHORIZATION"),
        ],
    }


@pytest.fixture
def mock_compose_export_path(monkeypatch, tmp_path):
    # files in tmp_dir will remain (in separate folders) for 3 sequential runs of pytest
    def mock_return(func_name, *args, **kwargs):
        return tmp_path / f"20220829_235959_{func_name}"

    monkeypatch.setattr("openbb_terminal.helper_funcs.compose_export_path", mock_return)


@pytest.mark.parametrize(
    "export_type, dir_path, func_name, df",
    [
        (
            "csv",
            "C:/openbb_terminal/common/behavioural_analysis",
            "queries",
            pd.DataFrame(),
        ),
        (
            "json",
            "C:/openbb_terminal/common/behavioural_analysis",
            "queries",
            pd.DataFrame(),
        ),
        (
            "xlsx",
            "C:/openbb_terminal/common/behavioural_analysis",
            "queries",
            pd.DataFrame(),
        ),
        (
            "png",
            "C:/openbb_terminal/common/behavioural_analysis",
            "queries",
            pd.DataFrame(),
        ),
        (
            "jpg",
            "C:/openbb_terminal/common/behavioural_analysis",
            "queries",
            pd.DataFrame(),
        ),
        (
            "pdf",
            "C:/openbb_terminal/common/behavioural_analysis",
            "queries",
            pd.DataFrame(),
        ),
        (
            "svg",
            "C:/openbb_terminal/common/behavioural_analysis",
            "queries",
            pd.DataFrame(),
        ),
    ],
)
def test_export_data_filetypes(
    mock_compose_export_path, export_type, dir_path, func_name, df, tmp_path
):
    export_data(export_type, dir_path, func_name, df)

    assert Path(tmp_path / f"20220829_235959_{func_name}.{export_type}").exists()
    # TODO add assertions to check the validity of the files?


@pytest.mark.parametrize(
    "export_type, dir_path, func_name, data",
    [
        (
            # Dict instead of DataFrame
            "csv",
            "C:/openbb_terminal/common/behavioural_analysis",
            "queries",
            dict({"test": "dict"}),
        ),
    ],
)
def test_export_data_invalid_data(
    mock_compose_export_path, export_type, dir_path, func_name, data
):
    with pytest.raises(AttributeError):
        assert export_data(export_type, dir_path, func_name, data)


def test_start_less_than_end():
    assert check_start_less_than_end("2022-01-01", "2022-01-02") is False
    assert check_start_less_than_end("2022-01-02", "2022-01-01") is True
    assert check_start_less_than_end("2022-01-01", "2022-01-01") is True
    assert check_start_less_than_end(None, "2022-01-01") is False
    assert check_start_less_than_end("2022-01-02", None) is False
    assert check_start_less_than_end(None, None) is False


@pytest.mark.parametrize(
    "df, df_expected",
    [
        (
            pd.DataFrame(
                {
                    "date1": pd.date_range("2021-01-01", periods=5, tz="Europe/London"),
                    "date2": pd.date_range("2022-01-01", periods=5, tz="Europe/London"),
                    "value1": [1, 2, 3, 4, 5],
                    "value2": [6, 7, 8, 9, 10],
                }
            ),
            pd.DataFrame(
                {
                    "date1": [
                        datetime.date(2021, 1, 1),
                        datetime.date(2021, 1, 2),
                        datetime.date(2021, 1, 3),
                        datetime.date(2021, 1, 4),
                        datetime.date(2021, 1, 5),
                    ],
                    "date2": [
                        datetime.date(2022, 1, 1),
                        datetime.date(2022, 1, 2),
                        datetime.date(2022, 1, 3),
                        datetime.date(2022, 1, 4),
                        datetime.date(2022, 1, 5),
                    ],
                    "value1": [1, 2, 3, 4, 5],
                    "value2": [6, 7, 8, 9, 10],
                }
            ),
        ),
    ],
)
def test_remove_timezone_from_dataframe(df, df_expected):
    # set date1 as index
    df.set_index("date1", inplace=True)
    df_expected.set_index("date1", inplace=True)

    df_result = remove_timezone_from_dataframe(df)
    assert df_result.equals(df_expected)


@pytest.mark.parametrize(
    "value, expected",
    [
        (123, 123),
        ("xpto", "xpto"),
        (
            "this isssssssssss a veryyyyy long stringgg",
            "this isssssssssss a veryyyyy long stringgg",
        ),
        (None, None),
        (True, True),
        (0, 0),
        ("2022-01-01", "2022-01-01"),
        ("3/9/2022", "3/9/2022"),
        ("2022-03-09 10:30:00", "2022-03-09 10:30:00"),
        ("a 123", "a 123"),
        ([1, 2, 3], [1, 2, 3]),
        ("", ""),
        ("-3 K", -3000.0),
        ("-99 M", -99000000.0),
        ("-125 B", -125000000000.0),
        ("-15 T", -15000000000000.0),
        ("-15 P", -15000000000000000.0),
        ("-15 P xpto", "-15 P xpto"),
        ("-15 P 3 K", "-15 P 3 K"),
        ("15 P -3 K", "15 P -3 K"),
        ("2.130", 2.130),
        ("2,130.000", "2,130.000"),  # this is not a valid number
        ("674,234.99", "674,234.99"),  # this is not a valid number
    ],
)
def test_revert_lambda_long_number_format(value, expected):
    assert revert_lambda_long_number_format(value) == expected


@pytest.mark.vcr
def test_update_news_from_tweet_to_be_displayed(mocker):
    preferences = PreferencesModel(
        TOOLBAR_TWEET_NEWS=True,
        TOOLBAR_TWEET_NEWS_SECONDS_BETWEEN_UPDATES=300,
        TOOLBAR_TWEET_NEWS_NUM_LAST_TWEETS_TO_READ=3,
        TOOLBAR_TWEET_NEWS_KEYWORDS="BREAKING,JUST IN",
    )
    mock_current_user = copy_user(preferences=preferences)
    mocker.patch(
        target="openbb_terminal.core.session.current_user.__current_user",
        new=mock_current_user,
    )
    mocker.patch(
        target="openbb_terminal.helper_funcs.LAST_TWEET_NEWS_UPDATE_CHECK_TIME",
        new=None,
    )
    news_tweet = update_news_from_tweet_to_be_displayed()
    assert isinstance(news_tweet, str) and news_tweet != ""
