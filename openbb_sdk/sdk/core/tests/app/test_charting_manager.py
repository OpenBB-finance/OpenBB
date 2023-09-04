"""Test charting manager."""
import pytest
from openbb_core.app.charting_manager import ChartingManager
from openbb_core.app.model.system_settings import SystemSettings
from openbb_core.app.model.user_settings import UserSettings


@pytest.fixture(scope="function", autouse=True)
def setup_and_teardown():
    """Prepare test context."""
    # Code to run before each test function
    yield  # This is where the test function runs
    # Code to run after each test function
    ChartingManager._instances = {}  # pylint: disable=protected-access


def test_charting_manager():
    """Smoke test."""
    assert ChartingManager() is not None


def test_charting_manager_singleton_prop():
    """Smoke test."""
    cm_1 = ChartingManager()
    cm_2 = ChartingManager()

    assert cm_1 is cm_2


def test_charting_settings():
    """Test helper."""
    sys = SystemSettings(test_mode=True)
    user = UserSettings(preferences={"plot_enable_pywry": False})

    cm = ChartingManager(user_settings=user, system_settings=sys)

    assert cm.charting_settings.plot_enable_pywry is False
    assert cm.charting_settings.test_mode is True


def test_charting_settings_setter():
    """Test helper."""
    cm = ChartingManager()

    sys = SystemSettings(test_mode=True)
    user = UserSettings(preferences={"plot_enable_pywry": False})

    cm.charting_settings = (sys, user)

    assert cm.charting_settings.plot_enable_pywry is False
    assert cm.charting_settings.test_mode is True


def test_check_charting_extension_installed():
    """Test helper."""
    cm = ChartingManager()

    try:
        import openbb_charting  # pylint: disable=unused-import,import-outside-toplevel  # noqa: F401,E501

        assert cm.check_charting_extension_installed("charting") is True
    except ImportError:
        assert cm.check_charting_extension_installed("charting") is False
    assert cm.check_charting_extension_installed("openbb_core_extension_2") is False
