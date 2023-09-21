from unittest.mock import patch

import pytest
from openbb_core.app.charting_service import ChartingService, ChartingServiceError
from openbb_core.app.model.system_settings import SystemSettings
from openbb_core.app.model.user_settings import UserSettings


@pytest.fixture(autouse=True)
def setup_and_teardown():
    # Code to run before each test function
    yield  # This is where the test function runs
    # Code to run after each test function
    ChartingService._instances = {}


# fixture for system_settings
@pytest.fixture()
def system_settings():
    return SystemSettings()


# fixture for user_settings
@pytest.fixture()
def user_settings():
    return UserSettings()


# fixture for charting_service
@pytest.fixture()
def charting_service(user_settings, system_settings):
    return ChartingService(user_settings=user_settings, system_settings=system_settings)


def test_charting_service(user_settings, system_settings):
    assert ChartingService(user_settings=user_settings, system_settings=system_settings)


def test_charting_service_singleton_prop(user_settings, system_settings):
    cm_1 = ChartingService(user_settings=user_settings, system_settings=system_settings)
    cm_2 = ChartingService(user_settings=user_settings, system_settings=system_settings)

    assert cm_1 is cm_2


def test_charting_settings():
    sys = SystemSettings(test_mode=True)
    user = UserSettings(preferences={"plot_enable_pywry": False})

    cm = ChartingService(user_settings=user, system_settings=sys)

    assert cm.charting_settings.plot_enable_pywry is False
    assert cm.charting_settings.test_mode is True


def test_charting_settings_setter(charting_service):
    sys = SystemSettings(test_mode=True)
    user = UserSettings(preferences={"plot_enable_pywry": False})

    charting_service.charting_settings = (sys, user)

    assert charting_service.charting_settings.plot_enable_pywry is False
    assert charting_service.charting_settings.test_mode is True


@pytest.mark.parametrize(
    "user_preferences_charting_extension, expected_result",
    [
        ("openbb_charting", "openbb_charting"),  # Matching extension names
        ("openbb_charting", ChartingServiceError),  # Mismatching extension names
    ],
)
def test_check_and_get_charting_extension_name(
    system_settings, user_preferences_charting_extension, expected_result
):
    user = UserSettings(
        preferences={"charting_extension": user_preferences_charting_extension}
    )
    cm = ChartingService(user_settings=user, system_settings=system_settings)

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
    mock_entry_points, charting_service, charting_extension, expected_result
):
    class MockEntryPoint:
        def __init__(self, name):
            self.name = name

    mock_entry_points.return_value = [MockEntryPoint("mock_extension")]

    # Call the function and assert the result
    result = charting_service._check_charting_extension_installed(charting_extension)
    assert result == expected_result


@pytest.mark.parametrize(
    "extension_name, expected_result",
    [
        ("mock_extension", "mock_module"),
        ("another_extension", ChartingServiceError),
    ],
)
@patch("openbb_core.app.charting_service.import_module")
@patch("openbb_core.app.charting_service.entry_points")
def test_get_extension_router(
    mock_entry_points,
    mock_import_module,
    charting_service,
    extension_name,
    expected_result,
):
    class MockEntryPoint:
        def __init__(self, name, module):
            self.name = name
            self.module = module

    mock_entry_points.return_value = [MockEntryPoint("mock_extension", "mock_module")]
    mock_import_module.return_value = "mock_module"

    if expected_result == ChartingServiceError:
        with pytest.raises(ChartingServiceError) as exc_info:
            charting_service._get_extension_router(extension_name)
            assert str(exc_info.value) == (
                f"Extension '{extension_name}' is not installed."
            )
    else:
        result = charting_service._get_extension_router("mock_extension")
        assert result == "mock_module"


@patch("openbb_core.app.charting_service.import_module")
def test_handle_back_end(mock_import_module, charting_service):
    class MockBackend:
        def __init__(self):
            pass

        def start(self, debug):
            pass

    class MockBackendModule:
        def __init__(self):
            self._backend = None

        def create_backend(self, charting_settings):
            self._backend = MockBackend()

        def get_backend(self):
            return self._backend

    mock_import_module.return_value = MockBackendModule()
    assert (
        charting_service._handle_backend(
            "mock_extension", charting_service.charting_settings
        )
        is None
    )


@patch("openbb_core.app.charting_service.ChartingService._get_extension_router")
def test_get_chart_format(mock_get_extension_router, charting_service):
    class MockChartingRouterModule:
        CHART_FORMAT = "mock_chart_format"

    mock_get_extension_router.return_value = MockChartingRouterModule()

    assert charting_service._get_chart_format("mock_extension") == "mock_chart_format"
