# IMPORTATION STANDARD
from pathlib import Path

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal import feature_flags as obbff


# pylint: disable=E1101
# pylint: disable=W0603
# pylint: disable=E1111
# pylint: disable=W0621
# pylint: disable=W0613


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


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "data",
    [
        dict({"A": [1, 2, 3], "B": [4, 5, 6]}),
        dict({"A": [1, "hello", 0], "B": ["0 sd", -5, 6]}),
    ],
)
def test_print_rich_table(data):

    df = pd.DataFrame(data)

    print_rich_table(df)


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "automatic_coloring,columns_to_auto_color,rows_to_auto_color",
    [
        (False, None, None),
        (True, None, None),
        (False, ["A"], None),
        (True, ["A"], None),
        (True, ["D", 0], None),
        (True, ["A", "B"], None),
        (False, None, ["first"]),
        (True, None, ["first"]),
        (True, None, ["first", 3]),
        (True, None, ["first", 2]),
        (True, ["A", "B"], ["first", "second", 2]),
    ],
)
def test_print_rich_table_coloring(
    mocker, automatic_coloring, columns_to_auto_color, rows_to_auto_color
):
    mocker.patch.object(target=obbff, attribute="USE_TABULATE_DF", new=False)
    mocker.patch.object(target=obbff, attribute="USE_COLOR", new=True)

    mocker.patch("openbb_terminal.helper_funcs.obbff.USE_TABULATE_DF", False)
    mocker.patch("openbb_terminal.helper_funcs.obbff.USE_COLOR", True)

    # create dummy dataframe
    df = pd.DataFrame(data=dict({"A": ["1", "123", "0"], "B": ["0", "-5", "6"]}))
    # change index
    df.index = ["first", "second", 2]

    print(automatic_coloring)
    print(columns_to_auto_color)
    print(rows_to_auto_color)

    print_rich_table(
        df,
        automatic_coloring=automatic_coloring,
        columns_to_auto_color=columns_to_auto_color,
        rows_to_auto_color=rows_to_auto_color,
    )
