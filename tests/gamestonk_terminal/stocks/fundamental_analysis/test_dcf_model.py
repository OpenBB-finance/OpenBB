# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import openpyxl
import numpy as np
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.fundamental_analysis import dcf_model, dcf_static


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("period1", "1598220000"),
            ("period2", "1635980400"),
        ],
    }


@pytest.mark.parametrize(
    "string, expected",
    [
        ("", 0),
        ("  12-345,067  ", 12345067.0),
    ],
)
def test_string_float(string: str, expected: float):
    assert dcf_model.string_float(string) == expected


def test_insert_row():
    df = pd.DataFrame(
        data={"col1": [1, 2], "col2": [3, 4]},
        index=["one", "two"],
    )
    result_df = dcf_model.insert_row(
        name="three",
        index="two",
        df=df,
        row_v=[5, 6],
    )

    expected_df = pd.DataFrame(
        data={"col1": [1, 2, 5], "col2": [3, 4, 6]},
        index=["one", "two", "three"],
    )

    assert not result_df.empty
    pd.testing.assert_frame_equal(result_df, expected_df)


def test_insert_row_unchanged():
    df = pd.DataFrame(
        data={"col1": [1, 2], "col2": [3, 4]},
        index=["one", "two"],
    )
    expected_df = df.copy()
    result_df = dcf_model.insert_row(
        name="one",
        index="two",
        df=df,
        row_v=[5, 6],
    )

    assert not result_df.empty
    pd.testing.assert_frame_equal(result_df, expected_df)


def test_set_cell():
    workbook = openpyxl.Workbook()
    worksheet = workbook.active

    dcf_model.set_cell(
        ws=worksheet,
        cell="A1",
        text="some content",
        font=dcf_static.bold_font,
        fill=dcf_static.green_bg,
        border=dcf_static.thin_border_nr,
        alignment=dcf_static.center,
        num_form=dcf_static.fmt_acct,
    )
    assert worksheet["A1"].value == "some content"


@pytest.mark.vcr
def test_get_fama_raw(recorder):
    result_df = dcf_model.get_fama_raw()

    recorder.capture(result_df)


@pytest.mark.vcr
def test_get_historical_5(recorder):
    result_df = dcf_model.get_historical_5(ticker="TSLA")

    recorder.capture(result_df)


@pytest.mark.vcr
def test_get_fama_coe():
    coef = dcf_model.get_fama_coe(ticker="TSLA")

    assert isinstance(coef, np.float64)


@pytest.mark.vcr
def test_others_in_sector():
    data = dcf_model.others_in_sector(
        ticker="PM", sector="Consumer Defensive", industry="Tobacco"
    )
    assert len(data) > 0
