import argparse
from typing import List

import pandas as pd
import pytest

from openbb_terminal.core.models.preferences_model import PreferencesModel
from openbb_terminal.core.session.current_user import copy_user
from openbb_terminal.custom_prompt_toolkit import NestedCompleter

try:
    from openbb_terminal.forecast import forecast_controller as fc
except ImportError:
    pytest.skip(allow_module_level=True)

# pylint: disable=E1121
base = "openbb_terminal.forecast.forecast_controller."
the_list = [[x + 1, x + 2, x + 3] for x in range(50)]
df = pd.DataFrame(the_list, columns=["first", "date", "close"])


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


def test_forecast_controller(mocker):
    mocker.patch(base + "session", True)
    preferences = PreferencesModel(USE_PROMPT_TOOLKIT=True)
    mock_current_user = copy_user(preferences=preferences)
    mocker.patch(
        target="openbb_terminal.core.session.current_user.__current_user",
        new=mock_current_user,
    )
    cont = fc.ForecastController(data=df, ticker="TSLA")
    assert isinstance(cont.files, List)


def test_fc_update_runtime_choices(mocker):
    mocker.patch(base + "session", True)
    preferences = PreferencesModel(USE_PROMPT_TOOLKIT=True)
    mock_current_user = copy_user(preferences=preferences)
    mocker.patch(
        target="openbb_terminal.core.session.current_user.__current_user",
        new=mock_current_user,
    )
    cont = fc.ForecastController()
    cont.datasets = {"stonks": df}
    cont.update_runtime_choices()
    assert isinstance(cont.completer, NestedCompleter)


def test_fc_refresh_datasets_on_menu():
    cont = fc.ForecastController()
    cont.datasets = {"stonks": df}
    cont.files = ["file.csv", "fiile.csv"]
    cont.refresh_datasets_on_menu()
    assert "stonks.first" in cont.list_dataset_cols


def test_fc_print_help(capsys):
    cont = fc.ForecastController()
    cont.print_help()
    captured = capsys.readouterr()
    assert "ll models are for educational purposes " in captured.out


def test_fc_custom_reset():
    cont = fc.ForecastController()
    val = cont.custom_reset()
    assert not val


def test_fc_custom_reset_with_files():
    cont = fc.ForecastController()
    cont.files_full = [["file1", "file1"]]
    val = cont.custom_reset()
    assert val == ["forecast", "'load file1 -a file1'"]


def test_fc_call_load(mocker):
    mocker.patch("openbb_terminal.common.common_model.load", return_value=df)
    cont = fc.ForecastController()
    cont.call_load(["data.csv"])


def test_fc_call_load_alias():
    cont = fc.ForecastController()
    cont.files = ["the_data"]
    cont.call_load(["data.csv", "-a", "the_data"])


def test_fc_call_load_alias_no_dot():
    cont = fc.ForecastController()
    cont.call_load(["datacsv", "-a", "the_data"])


@pytest.mark.parametrize(
    "name,loc_df", [("base", df), ("base", pd.DataFrame()), ("", df)]
)
def test_fc_call_show(mocker, name, loc_df):
    mock = mocker.MagicMock()
    mock.name = name
    mock.limit = 4
    mock.limit_col = 9
    mocker.patch(
        base + "ForecastController.parse_known_args_and_warn", return_value=mock
    )
    cont = fc.ForecastController()
    cont.datasets = {"base": loc_df}
    cont.call_show(["data"])


@pytest.mark.parametrize("dataset", ["base", None])
def test_call_desc(mocker, dataset):
    mock = mocker.MagicMock()
    mock.target_dataset = dataset
    mocker.patch(
        base + "ForecastController.parse_known_args_and_warn", return_value=mock
    )
    cont = fc.ForecastController()
    cont.datasets = {"base": df}
    cont.call_desc(["data"])


def test_call_plot(mocker):
    mock = mocker.MagicMock()
    mock.values = "data.first"
    mocker.patch(
        base + "ForecastController.parse_known_args_and_warn", return_value=mock
    )
    cont = fc.ForecastController()
    cont.choices = {"plot": ["data.first", "data.second", "data.third"]}
    cont.datasets = {"data": df}
    cont.call_plot(["data.first"])


def test_call_plot_no_parser(mocker):
    mocker.patch(
        base + "ForecastController.parse_known_args_and_warn", return_value=None
    )
    cont = fc.ForecastController()
    cont.choices = {"plot": ["data.first", "data.second", "data.third"]}
    cont.datasets = {"data": df}
    cont.call_plot(["data.first"])


def test_call_plot_no_values(mocker):
    mock = mocker.MagicMock()
    mock.values = None
    mocker.patch(
        base + "ForecastController.parse_known_args_and_warn", return_value=mock
    )
    cont = fc.ForecastController()
    cont.choices = {"plot": ["data.first", "data.second", "data.third"]}
    cont.datasets = {"data": df}
    cont.call_plot(["data.first"])


def test_call_season(tsla_csv):
    cont = fc.ForecastController()
    cont.datasets = {"data": tsla_csv}
    cont.call_season(["data.close", "--max_lag", "1"])


def test_call_season_error():
    cont = fc.ForecastController()
    cont.datasets = {"data": df}
    cont.call_season(["datafirst", "--max_lag", "1"])


def test_call_season_no_parser(mocker):
    mocker.patch(
        base + "ForecastController.parse_known_args_and_warn", return_value=None
    )
    cont = fc.ForecastController()
    cont.datasets = {"data": df}
    cont.call_season(["data.first", "--max_lag", "1"])


def test_call_season_no_values(mocker):
    mock = mocker.MagicMock()
    mock.values = None
    mocker.patch(
        base + "ForecastController.parse_known_args_and_warn", return_value=mock
    )
    cont = fc.ForecastController()
    cont.datasets = {"data": df}
    cont.call_season(["data.first", "--max_lag", "1"])


def test_call_corr():
    cont = fc.ForecastController()
    cont.datasets = {"data": df}
    cont.call_corr(["data"])


def test_call_corr_target(mocker):
    mock = mocker.MagicMock()
    mock.target_dataset = None
    mocker.patch(
        base + "ForecastController.parse_known_args_and_warn", return_value=mock
    )
    cont = fc.ForecastController()
    cont.datasets = {"data": df}
    cont.call_corr(["data"])


def test_call_comb_not_in(mocker):
    mock = mocker.MagicMock()
    mock.values = ["data.first"]
    mocker.patch(
        base + "ForecastController.parse_known_args_and_warn", return_value=mock
    )
    cont = fc.ForecastController()
    cont.datasets = {"data": df}
    cont.choices = {
        "combine": {"data.first": 1, "data.second": 2, "data.third": 3},
        "delete": {"data.first": 1, "data.second": 2, "data.third": 3},
    }
    cont.call_combine(["data"])


@pytest.mark.skip
def test_call_comb(mocker):
    mock = mocker.MagicMock()
    mock.dataset = "data"
    mock.columns = "data.close"
    mocker.patch(
        base + "ForecastController.parse_known_args_and_warn", return_value=mock
    )
    cont = fc.ForecastController()
    cont.datasets = {"data": df}
    cont.choices = {
        "combine": {"data.first": 1, "data.second": 2, "data.third": 3},
        "delete": {"data.first": 1, "data.second": 2, "data.third": 3},
    }

    cont.call_combine(["--dataset", "data", "--columns", "data.first"])


def test_call_clean():
    cont = fc.ForecastController()
    cont.datasets = {"data": df}
    cont.call_clean(["data"])


def test_call_clean_bad(mocker):
    mock = mocker.MagicMock()
    mock.target_dataset = None
    mocker.patch(
        base + "ForecastController.parse_known_args_and_warn", return_value=mock
    )
    cont = fc.ForecastController()
    cont.datasets = {"data": df}
    cont.call_clean(["data"])


@pytest.mark.parametrize(
    "feature", ["ema", "sto", "rsi", "roc", "mom", "delta", "atr", "signal", "delete"]
)
def test_call_feat_eng_invalid(feature):
    cont = fc.ForecastController()
    cont.datasets = {"data": df}
    cont.files = ["file.csv", "fiile.csv"]
    cont.choices = {
        "combine": {"data.first": 1, "data.second": 2, "data.third": 3},
        "delete": {"data.first": 1, "data.second": 2, "data.third": 3},
    }
    a_list = ["data"]
    if feature == "rsi":
        a_list.append("--period")
        a_list.append("2")
    getattr(cont, f"call_{feature}")(a_list)


@pytest.mark.parametrize(
    "feature",
    ["ema", "sto", "rsi", "roc", "mom", "delta", "atr", "signal", "export"],
)
def test_call_feat_eng_invalid_parser(feature, mocker):
    mocker.patch(base + "helpers.check_parser_input", return_value=None)
    mock = mocker.MagicMock()
    mock.target_dataset = None
    mocker.patch(
        base + "ForecastController.parse_known_args_and_warn", return_value=mock
    )
    cont = fc.ForecastController()
    cont.datasets = {"data": df}
    cont.files = ["file.csv", "fiile.csv"]
    cont.choices = {
        "combine": {"data.first": 1, "data.second": 2, "data.third": 3},
        "delete": {"data.first": 1, "data.second": 2, "data.third": 3},
    }
    a_list = ["data"]
    if feature == "rsi":
        a_list.append("--period")
        a_list.append("2")
    getattr(cont, f"call_{feature}")(a_list)


def test_call_ema(mocker):
    mock = mocker.MagicMock()
    mock.target_dataset = "data"
    mock.columns = ["data.first", "data.second"]
    mocker.patch(
        base + "ForecastController.parse_known_args_and_warn", return_value=mock
    )
    cont = fc.ForecastController()
    cont.datasets = {"data": df}
    cont.call_ema(["data"])


# TODO: for now we are not allowing multiple items in the split
@pytest.mark.skip
@pytest.mark.parametrize("datasets", [[], ["data"], ["bad"]])
def test_call_delete(mocker, datasets):
    cont = fc.ForecastController()
    mock = mocker.MagicMock()
    if datasets == ["bad"]:
        mock.delete = ["data.lose"]
    else:
        mock.delete = ["data.close"]
    mocker.patch(
        base + "ForecastController.parse_known_args_and_warn", return_value=mock
    )
    if datasets == ["data"]:
        cont.datasets = {"data": df}
    cont.choices = {
        "combine": ["data.first", "data.second", "data.third"],
        "delete": ["data.first", "data.second", "data.third"],
    }
    cont.call_delete([])


def test_call_export(mocker):
    mock = mocker.MagicMock()
    mock.target_dataset = "data"
    mock.columns = ["data.first", "data.second"]
    mocker.patch(
        base + "ForecastController.parse_known_args_and_warn", return_value=mock
    )
    cont = fc.ForecastController()
    cont.datasets = {"data": df}
    cont.call_export(["data"])


@pytest.mark.parametrize(
    "opt, func",
    [
        ("expo", "expo_view.display_expo_forecast"),
        ("theta", "theta_view.display_theta_forecast"),
        ("rnn", "rnn_view.display_rnn_forecast"),
        ("nbeats", "nbeats_view.display_nbeats_forecast"),
        ("tcn", "tcn_view.display_tcn_forecast"),
        ("regr", "regr_view.display_regression"),
        ("linregr", "linregr_view.display_linear_regression"),
        ("brnn", "brnn_view.display_brnn_forecast"),
        ("trans", "trans_view.display_trans_forecast"),
        ("tft", "tft_view.display_tft_forecast"),
    ],
)
def test_models(mocker, opt, func):
    mocker.patch(base + "helpers.check_parser_input", return_value=True)
    mocker.patch(base + func)
    cont = fc.ForecastController()
    cont.datasets = {"data": df}
    getattr(cont, f"call_{opt}")(["data"])


@pytest.mark.parametrize(
    "opt",
    [
        "expo",
        "theta",
        "rnn",
        "nbeats",
        "tcn",
        "regr",
        "linregr",
        "brnn",
        "trans",
        "tft",
    ],
)
def test_models_bad(opt):
    cont = fc.ForecastController()
    cont.datasets = {"data": df}
    getattr(cont, f"call_{opt}")(["data"])
