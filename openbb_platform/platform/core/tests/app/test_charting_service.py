import pytest
from openbb_core.app.charting_service import ChartingService
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


@pytest.mark.skip(reason="function needs review")
def test_check_charting_extension_installed():
    sys = SystemSettings()
    user = UserSettings()
    cm = ChartingService(user_settings=user, system_settings=sys)

    assert cm._check_charting_extension_installed("openbb_charting") is True
    assert cm._check_charting_extension_installed("openbb_core_extension_2") is False
