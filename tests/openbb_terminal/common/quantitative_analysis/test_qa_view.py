from datetime import datetime, timedelta
from unittest.mock import MagicMock
import pytest
import pandas as pd

from openbb_terminal.common.quantitative_analysis import qa_view

dates = [datetime.now() - timedelta(days=x) for x in range(10)]
nums = list(range(1, 11))
data = {"date": dates, "col2": nums, "col1": [x - timedelta(days=1) for x in dates]}
data2 = {"date": nums, "col2": nums, "col1": dates}
df = pd.DataFrame(data).set_index("date")
df2 = pd.DataFrame(data2).set_index("date")
series = pd.Series(dict(zip(dates, nums)), name="Series")


@pytest.mark.parametrize("val", [0.04, 1])
def test_lambda_color_red(val):
    qa_view.lambda_color_red(val)


def test_display_summary():
    qa_view.display_summary(pd.DataFrame(data, columns=["col1", "col2"]), "xlsx")


@pytest.mark.parametrize("df_use, external", [(df, None), (df2, None), (df, [1, 2])])
def test_display_hist(df_use, external):
    qa_view.display_hist(df_use, "col2", "Data", 2, external)


def test_display_hist_fail():
    with pytest.raises(Exception):
        qa_view.display_hist(df, "col1", "Data", 2, [MagicMock()])


@pytest.mark.parametrize("external", [None, [1, 2]])
def test_display_cdf(external):
    qa_view.display_cdf(df, "col2", "Data", "xlsx", external)


def test_display_cdf_fail():
    with pytest.raises(Exception):
        qa_view.display_cdf(df, "col1", "Data", 2, [MagicMock()])


@pytest.mark.parametrize(
    "external, yearly", [(None, False), (None, True), ([1, 2], False)]
)
def test_display_bw(external, yearly):
    qa_view.display_bw(df, "col2", "Data", yearly, external)


@pytest.mark.parametrize("external, yearly", [([1, 2], False)])
def test_display_acf(external, yearly):
    qa_view.display_acf(df2, "col2", "Data", yearly, external)


@pytest.mark.parametrize("external", [None, [1, 2]])
def test_display_qqplot(external):
    qa_view.display_qqplot(df, "col2", "Data", external)


def test_display_cusum():
    qa_view.display_cusum(df, "col2", 1, 1, None)


def test_display_cusum_fail():
    with pytest.raises(Exception):
        qa_view.display_cusum(df, "col2", 1, 1, [1, 2])


@pytest.mark.parametrize("yearly", [False, True])
def test_display_seasonal(yearly):
    qa_view.display_seasonal("Data", df, "col2", yearly, "xlsx", None)


def test_display_normality():
    qa_view.display_normality(df, "col2", "xlsx")


def test_display_unitroot():
    qa_view.display_unitroot(df, "col2", "c", "c")


@pytest.mark.parametrize("use_df", [df, series])
def test_display_raw(use_df):
    sort = "col1" if isinstance(use_df, pd.DataFrame) else ""
    qa_view.display_raw(use_df, sort)


@pytest.mark.parametrize("y, external", [(True, None), (False, None), (True, [1, 2])])
def test_display_line(y, external):
    qa_view.display_line(
        series,
        log_y=y,
        markers_lines=True,
        markers_scatter=dates,
        external_axes=external,
        title=True,
    )


def test_display_var():
    df["adjclose"] = df["col2"]
    qa_view.display_var(df, "TSLA", True, True, 50, True)
