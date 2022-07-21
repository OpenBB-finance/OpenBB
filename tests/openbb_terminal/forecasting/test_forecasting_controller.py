from mock import PropertyMock
from typing import List
import argparse
import pandas as pd
import pytest
from prompt_toolkit.completion import NestedCompleter
from openbb_terminal.forecasting import forecasting_controller as fc

base = "openbb_terminal.forecasting.forecasting_controller."
df = pd.DataFrame([[1, 2, 3], [2, 3, 4], [3, 4, 5]], columns=["first", "date", "third"])


class Thing:
    help = True

    def format_help(self):
        return "You need help"


def mock_func(_):
    return (Thing(), 2)


def test_check_greater_than_one():
    assert fc.check_greater_than_one(2) == 2


def test_check_greater_than_one_invalid():
    with pytest.raises(argparse.ArgumentTypeError):
        fc.check_greater_than_one(-2)


def test_forecasting_controller(mocker):
    mocker.patch(base + "session", True)
    mocker.patch(base + "obbff.USE_PROMPT_TOOLKIT", True)
    cont = fc.ForecastingController()
    assert isinstance(cont.files, List)


def test_fc_update_runtime_choices(mocker):
    mocker.patch(base + "session", True)
    mocker.patch(base + "obbff.USE_PROMPT_TOOLKIT", True)
    cont = fc.ForecastingController()
    cont.datasets = {"stonks": df}
    cont.update_runtime_choices()
    assert isinstance(cont.completer, NestedCompleter)


def test_fc_refresh_datasets_on_menu():
    cont = fc.ForecastingController()
    cont.datasets = {"stonks": df}
    cont.files = ["file.csv", "fiile.csv"]
    cont.refresh_datasets_on_menu()
    assert "stonks.first" in cont.list_dataset_cols


def test_fc_print_help(capsys):
    cont = fc.ForecastingController()
    cont.print_help()
    captured = capsys.readouterr()
    assert "forecasting" in captured.out


def test_fc_custom_reset():
    cont = fc.ForecastingController()
    val = cont.custom_reset()
    assert val == []


def test_fc_custom_reset_with_files():
    cont = fc.ForecastingController()
    cont.files = ["file1"]
    val = cont.custom_reset()
    assert val == ["forecasting", "load file1"]


def test_fc_parse_known_args_and_warn(mocker):
    mock = mocker.Mock()
    mock2 = mocker.Mock()
    mock.parse_known_args = mock_func
    mock.format_help = Thing().format_help
    mock.add_argument = mock2
    cont = fc.ForecastingController()
    cont.parse_known_args_and_warn(
        mock,
        [],
        0,
        True,
        1,
        [],
        True,
        True,
        5,
        True,
        True,
        "weekly",
        True,
        True,
        True,
        True,
        True,
        True,
        True,
        "the_models",
        True,
        True,
        0.05,
        3,
        True,
        True,
        True,
        4,
        True,
        True,
        True,
        True,
    )
    assert mock2.call_count == 29


def test_fc_call_load(mocker):
    mocker.patch(base + "forecasting_model.load", return_value=df)
    cont = fc.ForecastingController()
    cont.call_load(["data.csv"])


def test_fc_call_load_alias():
    cont = fc.ForecastingController()
    cont.files = ["the_data"]
    cont.call_load(["data.csv", "-a", "the_data"])


def test_fc_call_load_alias_no_dot():
    cont = fc.ForecastingController()
    cont.call_load(["datacsv", "-a", "the_data"])


@pytest.mark.parametrize(
    "name,loc_df", [("base", df), ("base", pd.DataFrame()), ("", df)]
)
def test_fc_call_show(mocker, name, loc_df):
    mock = mocker.MagicMock()
    mock.name = name
    mock.limit = 4
    mocker.patch(
        base + "ForecastingController.parse_known_args_and_warn", return_value=mock
    )
    cont = fc.ForecastingController()
    cont.datasets = {"base": loc_df}
    cont.call_show(["data"])


@pytest.mark.parametrize("dataset", ["base", None])
def test_call_desc(mocker, dataset):
    mock = mocker.MagicMock()
    mock.target_dataset = dataset
    mocker.patch(
        base + "ForecastingController.parse_known_args_and_warn", return_value=mock
    )
    cont = fc.ForecastingController()
    cont.datasets = {"base": df}
    cont.call_desc(["data"])


def test_call_plot(mocker):
    mock = mocker.MagicMock()
    mock.values = ["data.first"]
    mocker.patch(
        base + "ForecastingController.parse_known_args_and_warn", return_value=mock
    )
    cont = fc.ForecastingController()
    cont.choices = {"plot": ["data.first", "data.second", "data.third"]}
    cont.datasets = {"data": df}
    cont.call_plot(["data.first"])


def test_call_season():
    cont = fc.ForecastingController()
    cont.datasets = {"data": df}
    cont.call_season(["data.first", "--max_lag", "1"])


def test_call_season_error():
    cont = fc.ForecastingController()
    cont.datasets = {"data": df}
    cont.call_season(["datafirst", "--max_lag", "1"])


def test_call_season_no_parser(mocker):
    mocker.patch(
        base + "ForecastingController.parse_known_args_and_warn", return_value=None
    )
    cont = fc.ForecastingController()
    cont.datasets = {"data": df}
    cont.call_season(["data.first", "--max_lag", "1"])


def test_call_season_no_values(mocker):
    mock = mocker.MagicMock()
    mock.values = None
    mocker.patch(
        base + "ForecastingController.parse_known_args_and_warn", return_value=mock
    )
    cont = fc.ForecastingController()
    cont.datasets = {"data": df}
    cont.call_season(["data.first", "--max_lag", "1"])


def test_call_corr():
    cont = fc.ForecastingController()
    cont.datasets = {"data": df}
    cont.call_corr(["data"])


def test_call_corr_target(mocker):
    mock = mocker.MagicMock()
    mock.target_dataset = None
    mocker.patch(
        base + "ForecastingController.parse_known_args_and_warn", return_value=mock
    )
    cont = fc.ForecastingController()
    cont.datasets = {"data": df}
    cont.call_corr(["data"])


def test_call_comb_not_in(mocker):
    mock = mocker.MagicMock()
    mock.values = ["data.first"]
    mocker.patch(
        base + "ForecastingController.parse_known_args_and_warn", return_value=mock
    )
    cont = fc.ForecastingController()
    cont.datasets = {"data": df}
    cont.choices = {
        "combine": ["data.first", "data.second", "data.third"],
        "delete": ["data.first", "data.second", "data.third"],
    }
    cont.call_combine(["data"])


def test_call_comb(mocker):
    mock = mocker.MagicMock()
    mock.dataset = "data"
    mock.columns = ["data.first", "data.second"]
    mocker.patch(
        base + "ForecastingController.parse_known_args_and_warn", return_value=mock
    )
    cont = fc.ForecastingController()
    cont.datasets = {"data": df}
    cont.choices = {
        "combine": ["data.first", "data.second", "data.third"],
        "delete": ["data.first", "data.second", "data.third"],
    }
    cont.call_combine(["data"])


def test_call_clean():
    cont = fc.ForecastingController()
    cont.datasets = {"data": df}
    cont.call_clean(["data"])


def test_call_clean_bad(mocker):
    mock = mocker.MagicMock()
    mock.target_dataset = None
    mocker.patch(
        base + "ForecastingController.parse_known_args_and_warn", return_value=mock
    )
    cont = fc.ForecastingController()
    cont.datasets = {"data": df}
    cont.call_clean(["data"])


def test_call_ema_invalid():
    cont = fc.ForecastingController()
    cont.datasets = {"data": df}
    cont.call_ema(["data"])


def test_call_ema(mocker):
    mock = mocker.MagicMock()
    mock.target_dataset = "data"
    mock.columns = ["data.first", "data.second"]
    mocker.patch(
        base + "ForecastingController.parse_known_args_and_warn", return_value=mock
    )
    cont = fc.ForecastingController()
    cont.datasets = {"data": df}
    cont.call_ema(["data"])
