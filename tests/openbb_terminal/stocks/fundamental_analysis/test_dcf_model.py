# IMPORTATION STANDARD
from pathlib import Path

# IMPORTATION THIRDPARTY
import numpy as np
import openpyxl
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.fundamental_analysis import dcf_model, dcf_static


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
    result_df = dcf_model.get_historical_5(symbol="TSLA")

    recorder.capture(result_df)


@pytest.mark.vcr
def test_get_fama_coe():
    coef = dcf_model.get_fama_coe(symbol="TSLA")

    assert isinstance(coef, np.float64)


@pytest.mark.vcr
def test_others_in_sector():
    data = dcf_model.others_in_sector(
        symbol="PM",
        sector="Consumer Staples",
        industry_group="Food, Beverage & Tobacco",
        industry="Tobacco",
    )
    assert len(data) > 0


def test_clean_dataframes():
    df1 = pd.DataFrame(
        data={"col1": [1, 2], "col2": [3, 4]},
        index=["one", "two"],
    )
    df2 = pd.DataFrame(
        data={"col1": [1, 2, 3], "col2": [3, 4, 5]},
        index=["one", "two", "three"],
    )
    df3 = pd.DataFrame(
        data={"col1": [1, 2], "col2": [3, 4]},
        index=["one", "two"],
    )

    result = dcf_model.clean_dataframes(df1, df2, df3)

    assert len(result[0]) == 2
    assert len(result[1]) == 3
    assert len(result[2]) == 2


def test_frac():
    result = dcf_model.frac(1, 2)

    assert result == 0.5


def test_generate_path():
    result = dcf_model.generate_path(
        n=1,
        file_name="test_dcf_model",
    )

    assert isinstance(result, Path)
