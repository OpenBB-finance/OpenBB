import pytest
from openbb_core.app.charting_manager import ChartingManager
from openbb_core.app.model.system_settings import SystemSettings
from openbb_core.app.model.user_settings import UserSettings


@pytest.fixture(scope="function", autouse=True)
def setup_and_teardown():
    # Code to run before each test function
    yield  # This is where the test function runs
    # Code to run after each test function
    ChartingManager._instances = {}


def test_charting_manager():
    assert ChartingManager()


def test_charting_manager_singleton_prop():
    cm_1 = ChartingManager()
    cm_2 = ChartingManager()

    assert cm_1 is cm_2


def test_charting_settings():
    sys = SystemSettings(test_mode=True)
    user = UserSettings(preferences={"plot_enable_pywry": False})

    cm = ChartingManager(user_settings=user, system_settings=sys)

    assert cm.charting_settings.plot_enable_pywry is False
    assert cm.charting_settings.test_mode is True


def test_charting_settings_setter():
    cm = ChartingManager()

    sys = SystemSettings(test_mode=True)
    user = UserSettings(preferences={"plot_enable_pywry": False})

    cm.charting_settings = (sys, user)

    assert cm.charting_settings.plot_enable_pywry is False
    assert cm.charting_settings.test_mode is True


def test_check_charting_extension_installed():
    cm = ChartingManager()

    assert cm.check_charting_extension_installed("openbb_charting") is True
    assert cm.check_charting_extension_installed("openbb_core_extension_2") is False
