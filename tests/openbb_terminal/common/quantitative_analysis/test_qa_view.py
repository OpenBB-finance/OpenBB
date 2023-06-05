from datetime import datetime, timedelta
from unittest.mock import MagicMock

import numpy as np
import pandas as pd
import pytest

from openbb_terminal.common.quantitative_analysis import qa_view

dates = [datetime.now() - timedelta(days=x) for x in range(45)]
nums = np.random.rand(45)
data = {"date": dates, "col2": nums, "col1": [x - timedelta(days=1) for x in dates]}
data2 = {"date": nums, "col2": nums, "col1": dates}
fail_df = {"date": [(1, 2)], "col2": [], "col1": dates}
df = pd.DataFrame(data).set_index("date")
df2 = pd.DataFrame(data2).set_index("date")
series = pd.Series(dict(zip(dates, nums)), name="Series")


# pylint: disable=unsupported-assignment-operation


@pytest.mark.parametrize("val", [0.04, 1])
def test_lambda_color_red(val):
    qa_view.lambda_color_red(val)


def test_display_summary():
    qa_view.display_summary(pd.DataFrame(data, columns=["col1", "col2"]), "xlsx", None)


@pytest.mark.parametrize("df_use, external", [(df, False), (df2, False), (df, True)])
def test_display_hist(df_use, external):
    fig = qa_view.display_hist(df_use, "col2", "Data", 2, external)
    if external:
        assert fig.__class__.__name__ == "OpenBBFigure"
    else:
        assert fig.__class__.__name__ == "MagicMock"


def test_display_hist_fail():
    with pytest.raises(Exception):
        qa_view.display_hist(fail_df, "col1", "Data", 2, True)


@pytest.mark.parametrize("external", [False, True])
def test_display_cdf(external):
    fig = qa_view.display_cdf(df, "col2", "Data", "xlsx", None, external)
    assert fig.__class__.__name__ == "OpenBBFigure"


def test_display_cdf_fail():
    with pytest.raises(Exception):
        qa_view.display_cdf(fail_df, "col1", "Data", 2, [MagicMock()])


@pytest.mark.parametrize(
    "external, yearly", [(False, False), (False, True), (True, False)]
)
def test_display_bw(external, yearly):
    fig = qa_view.display_bw(df, "col2", "Data", yearly, external)
    if external:
        assert fig.__class__.__name__ == "OpenBBFigure"
    else:
        assert fig.__class__.__name__ == "MagicMock"


@pytest.mark.parametrize("external", [False, True])
def test_display_acf(external):
    fig = qa_view.display_acf(df, "col2", "Data", external_axes=external)
    if external:
        assert fig.__class__.__name__ == "OpenBBFigure"
    else:
        assert fig.__class__.__name__ == "MagicMock"


@pytest.mark.parametrize("external", [False, True])
def test_display_qqplot(external):
    fig = qa_view.display_qqplot(df, "col2", "Data", external)
    if external:
        assert fig.__class__.__name__ == "OpenBBFigure"
    else:
        assert fig.__class__.__name__ == "MagicMock"


def test_display_cusum():
    qa_view.display_cusum(df, "col2", 1, 1, False)


def test_display_cusum_fail():
    with pytest.raises(Exception):
        qa_view.display_cusum(fail_df, "col2", 1, 1, False)


@pytest.mark.parametrize("yearly", [False, True])
def test_display_seasonal(mocker, yearly):
    mocker.patch(
        "openbb_terminal.helper_funcs.ask_file_overwrite", return_value=(False, True)
    )
    qa_view.display_seasonal("Data", df, "col2", yearly, "xlsx", None)


def test_display_normality():
    qa_view.display_normality(df, "col2", "xlsx", None)


def test_display_unitroot():
    qa_view.display_unitroot(df, "col2", "c", "c")


@pytest.mark.parametrize("use_df", [df, series])
def test_display_raw(use_df):
    sort = "col1" if isinstance(use_df, pd.DataFrame) else ""
    qa_view.display_raw(use_df, sort)


@pytest.mark.parametrize("y, external", [(True, False), (False, False), (True, True)])
def test_display_line(y, external):
    fig = qa_view.display_line(
        series,
        log_y=y,
        markers_lines=dates,
        markers_scatter=dates,
        external_axes=external,
        title="Test",
    )
    if external:
        assert fig.__class__.__name__ == "OpenBBFigure"
    else:
        assert fig.__class__.__name__ == "MagicMock"


def test_display_var():
    df["adjclose"] = df["col2"]
    qa_view.display_var(df, "TSLA", True, True, 50, True)
