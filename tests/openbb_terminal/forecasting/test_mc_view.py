import pytest
from openbb_terminal.forecasting import mc_view

base = "openbb_terminal.forecasting.mc_view."


def test_display_mc_forecast(tsla_csv):
    tsla_csv = tsla_csv.set_index("date")
    mc_view.display_mc_forecast(tsla_csv["close"], 1, 2)


def test_display_mc_forecast_external_axis_valid(tsla_csv, mocker):
    mock = mocker.Mock()
    mocker.patch(base + "is_valid_axes_count", return_value=True)
    tsla_csv = tsla_csv.set_index("date")
    with pytest.raises(TypeError):
        mc_view.display_mc_forecast(tsla_csv["close"], 1, 2, external_axes=(mock, mock))


def test_display_mc_forecast_external_axis_invalid(tsla_csv, mocker):
    mocker.patch(base + "is_valid_axes_count", return_value=False)
    tsla_csv = tsla_csv.set_index("date")
    mc_view.display_mc_forecast(
        tsla_csv["close"], 1, 2, time_res="2D", external_axes=True
    )
