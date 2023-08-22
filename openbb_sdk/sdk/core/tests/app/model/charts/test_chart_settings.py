from unittest.mock import MagicMock, Mock, patch

from openbb_core.app.model.charts.charting_settings import ChartingSettings

mock_user_settings = MagicMock()
mock_user_settings.preferences.data_directory = "mock_data_directory"
mock_user_settings.preferences.plot_enable_pywry = True
mock_user_settings.preferences.plot_pywry_width = 100
mock_user_settings.preferences.plot_pywry_height = 100
mock_user_settings.preferences.plot_open_export = True
mock_user_settings.profile.hub_session.email = "mock_email"
mock_user_settings.profile.hub_session.user_uuid = "mock_uuid"
mock_user_settings.preferences.export_directory = "mock_export_directory"
mock_user_settings.preferences.user_styles_directory = "mock_styles_directory"
mock_user_settings.preferences.chart_style = "mock_chart_style"

mock_system_settings = MagicMock()
mock_system_settings.log_collect = True
mock_system_settings.version = "mock_version"
mock_system_settings.python_version = "mock_python_version"
mock_system_settings.test_mode = True
mock_system_settings.debug_mode = True
mock_system_settings.headless = True


@patch(
    target="openbb_core.app.model.charts.charting_settings.get_app_id",
    new=Mock(return_value="mock_app_id"),
)
def test_charting_settings():
    charting_settings = ChartingSettings(
        user_settings=mock_user_settings, system_settings=mock_system_settings
    )
    assert charting_settings.log_collect is True
    assert charting_settings.version == "mock_version"
    assert charting_settings.python_version == "mock_python_version"
    assert charting_settings.test_mode is True
    assert charting_settings.app_id == "mock_app_id"
    assert charting_settings.debug_mode is True
    assert charting_settings.headless is True
    assert charting_settings.plot_enable_pywry is True
    assert charting_settings.plot_pywry_width == 100
    assert charting_settings.plot_pywry_height == 100
    assert charting_settings.plot_open_export is True
    assert charting_settings.user_email == "mock_email"
    assert charting_settings.user_uuid == "mock_uuid"
    assert charting_settings.user_exports_directory == "mock_export_directory"
    assert charting_settings.user_styles_directory == "mock_styles_directory"
    assert charting_settings.chart_style == "mock_chart_style"
