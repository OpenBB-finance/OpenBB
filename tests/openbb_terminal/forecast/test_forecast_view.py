import matplotlib.pyplot as plt
import pandas as pd
import pytest

try:
    from openbb_terminal.forecast import forecast_view as fv
except ImportError:
    pytest.skip(allow_module_level=True)
base = "openbb_terminal.forecast.forecast_view."


def test_show_options_bad(capsys):
    fv.show_options({})
    captured = capsys.readouterr()
    assert "Please load" in captured.out


def test_show_options(tsla_csv, capsys):
    fv.show_options({"name": tsla_csv}, "name")
    captured = capsys.readouterr()
    assert "close" in captured.out


def test_display_plot(tsla_csv, mocker):
    mock = mocker.patch(base + "theme.visualize_output")
    fv.display_plot(tsla_csv, ["close"])
    mock.assert_called_once()


def test_display_plot_multiindex(tsla_csv, mocker):
    mock = mocker.patch(base + "theme.visualize_output")
    tuples = [("1", x) for x in tsla_csv.index]
    index = pd.MultiIndex.from_tuples(tuples, names=["first", "second"])
    tsla_csv.index = index
    fv.display_plot(tsla_csv, ["close"])
    mock.assert_called_once()


def test_display_plot_external_axes(tsla_csv, mocker):
    mock1 = mocker.Mock()
    mock = mocker.patch(base + "theme.visualize_output")
    fv.display_plot(tsla_csv, ["close"], external_axes=[mock1])
    mock.assert_not_called()


def test_display_plot_series(tsla_csv, mocker):
    mock1 = mocker.Mock()
    mock = mocker.patch(base + "theme.visualize_output")
    fv.display_plot(tsla_csv, ["close"], external_axes=[mock1])
    mock.assert_not_called()


def test_display_seasonality_external_axes(tsla_csv, mocker):
    mock1 = mocker.Mock()
    mock = mocker.patch(base + "theme.visualize_output")
    fv.display_seasonality(tsla_csv, external_axes=[mock1], column="close")
    mock.assert_not_called()


def test_display_seasonality(tsla_csv, mocker):
    mock = mocker.patch(base + "theme.visualize_output")
    fv.display_seasonality(tsla_csv, column="close")
    mock.assert_called_once()


def test_display_corr_external_axes(tsla_csv, mocker):
    _, ax = plt.subplots(dpi=20)
    mock = mocker.patch(base + "theme.visualize_output")
    fv.display_corr(tsla_csv, external_axes=[ax])
    mock.assert_not_called()


def test_display_corr(tsla_csv, mocker):
    mock = mocker.patch(base + "theme.visualize_output")
    fv.display_corr(tsla_csv)
    mock.assert_called_once()
