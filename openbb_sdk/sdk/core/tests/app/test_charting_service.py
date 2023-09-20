import pytest
from unittest.mock import patch
from openbb_core.app.charting_service import ChartingService, ChartingServiceError
from openbb_core.app.model.system_settings import SystemSettings
from openbb_core.app.model.user_settings import UserSettings


@pytest.fixture(scope="function", autouse=True)
def setup_and_teardown():
    # Code to run before each test function
    yield  # This is where the test function runs
    # Code to run after each test function
    ChartingService._instances = {}


def test_charting_service():
    sys = SystemSettings()
    user = UserSettings()

    assert ChartingService(user_settings=user, system_settings=sys)


def test_charting_service_singleton_prop():
    sys = SystemSettings()
    user = UserSettings()

    cm_1 = ChartingService(user_settings=user, system_settings=sys)
    cm_2 = ChartingService(user_settings=user, system_settings=sys)

    assert cm_1 is cm_2


def test_charting_settings():
    sys = SystemSettings(test_mode=True)
    user = UserSettings(preferences={"plot_enable_pywry": False})

    cm = ChartingService(user_settings=user, system_settings=sys)

    assert cm.charting_settings.plot_enable_pywry is False
    assert cm.charting_settings.test_mode is True


def test_charting_settings_setter():
    sys = SystemSettings()
    user = UserSettings()
    cm = ChartingService(user_settings=user, system_settings=sys)

    sys = SystemSettings(test_mode=True)
    user = UserSettings(preferences={"plot_enable_pywry": False})

    cm.charting_settings = (sys, user)

    assert cm.charting_settings.plot_enable_pywry is False
    assert cm.charting_settings.test_mode is True


@pytest.mark.parametrize(
    "user_preferences_charting_extension, expected_result",
    [
        ("openbb_charting", "openbb_charting"),  # Matching extension names
        ("openbb_charting", ChartingServiceError),  # Mismatching extension names
    ],
)
def test_check_and_get_charting_extension_name(
    user_preferences_charting_extension, expected_result
):
    sys = SystemSettings()
    user = UserSettings(
        preferences={"charting_extension": user_preferences_charting_extension}
    )
    cm = ChartingService(user_settings=user, system_settings=sys)

    if expected_result == ChartingServiceError:
        with pytest.raises(ChartingServiceError) as exc_info:
            # patch EXTENSION_NAME
            with patch(
                "openbb_core.app.charting_service.EXTENSION_NAME", "other_extension"
            ):
                cm._check_and_get_charting_extension_name(
                    user_preferences_charting_extension
                )
                assert str(exc_info.value) == (
                    f"The charting extension defined on user preferences must be the same as the one defined in the env file."
                    f"diff: {user_preferences_charting_extension} != openbb_charting"
                )
    else:
        with patch(
            "openbb_core.app.charting_service.EXTENSION_NAME", "openbb_charting"
        ):
            result = cm._check_and_get_charting_extension_name(
                user_preferences_charting_extension
            )
            assert result == expected_result


@patch("openbb_core.app.charting_service.entry_points")
@pytest.mark.parametrize(
    "charting_extension, expected_result",
    [
        ("mock_extension", True),  # Extension exists
        ("another_extension", False),  # Extension doesn't exist
    ],
)
def test_check_charting_extension_installed(
    mock_entry_points, charting_extension, expected_result
):
    class MockEntryPoint:
        def __init__(self, name):
            self.name = name

    sys = SystemSettings()
    user = UserSettings()
    cm = ChartingService(user_settings=user, system_settings=sys)

    mock_entry_points.return_value = [MockEntryPoint("mock_extension")]

    # Call the function and assert the result
    result = cm._check_charting_extension_installed(charting_extension)
    assert result == expected_result
