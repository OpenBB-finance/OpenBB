from unittest.mock import patch, Mock
import pandas as pd
from gamestonk_terminal import helper_funcs


@patch("gamestonk_terminal.feature_flags.ENABLE_AUTOSAVE", False)
def test_local_download_autosave_off():
    df = Mock(pd.DataFrame, create=True)
    helper_funcs.local_download(df, "csv")
    assert df.to_csv.call_count == 0


@patch("os.path.exists")
def test_local_download_invalid_path(path_mock):
    path_mock.return_value = False
    df = Mock(pd.DataFrame, create=True)
    helper_funcs.local_download(df, "csv")
    assert df.to_csv.call_count == 0


@patch("gamestonk_terminal.feature_flags.ENABLE_AUTOSAVE", True)
@patch("gamestonk_terminal.feature_flags.AUTOSAVE_DIRECTORY", "autosave-dir")
@patch("os.path.exists")
def test_local_download_valid_path(path_mock):
    path_mock.return_value = True
    df = Mock(pd.DataFrame, create=True)
    df.name = "df-name"
    helper_funcs.local_download(df, "csv")
    assert df.to_csv.call_count == 1
    assert "autosave-dir" in df.to_csv.call_args[0][0]
    assert "df-name" in df.to_csv.call_args[0][0]


@patch("gamestonk_terminal.feature_flags.ENABLE_AUTOSAVE", True)
@patch("matplotlib.pyplot.savefig")
@patch("os.path.exists")
def test_local_download_extensions(path_mock, savefig_mock):
    path_mock.return_value = True
    df = Mock(pd.DataFrame, create=True)
    helper_funcs.local_download(df, "csv")
    assert df.to_csv.call_count == 1

    helper_funcs.local_download(df, "json")
    assert df.to_json.call_count == 1

    helper_funcs.local_download(df, "xlsx")
    assert df.to_excel.call_count == 1

    helper_funcs.local_download(df, "png")
    helper_funcs.local_download(df, "jpg")
    helper_funcs.local_download(df, "pdf")
    helper_funcs.local_download(df, "svg")
    assert savefig_mock.call_count == 4


@patch("gamestonk_terminal.helper_funcs.local_download")
def test_print_rich_table(local_download_mock):
    df = Mock(pd.DataFrame, create=True)
    helper_funcs.print_rich_table(df)

    assert local_download_mock.called_once_with(df, "csv")
