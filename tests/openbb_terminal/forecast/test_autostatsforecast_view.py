import pytest

try:
    from openbb_terminal.forecast import autostatsforecast_view
except ImportError:
    pytest.skip(allow_module_level=True)


def test_display_autostatsforecast_forecast(tsla_csv):
    with pytest.raises(AttributeError):
        autostatsforecast_view.display_autostatsforecast_forecast(
            tsla_csv,
            target_column="close",
            seasonal_periods=3,
            n_predict=1,
            start_window=0.5,
            forecast_horizon=1,
        )
