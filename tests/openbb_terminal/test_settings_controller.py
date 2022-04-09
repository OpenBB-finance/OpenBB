import pytest

from openbb_terminal.settings_controller import SettingsController


def get_controller(mocker):
    mocker.patch(
        "openbb_terminal.settings_controller.obbff.USE_PROMPT_TOOLKIT",
        True,
    )
    mocker.patch("openbb_terminal.settings_controller.session", True)
    mocker.patch("openbb_terminal.settings_controller.set_key")
    return SettingsController()


def test_print_help(mocker):
    controller = get_controller(mocker)
    controller.print_help()


def test_call_logcollection(mocker):
    controller = get_controller(mocker)
    controller.call_logcollection(None)


def test_call_tab(mocker):
    controller = get_controller(mocker)
    controller.call_tab(None)


def test_call_cls(mocker):
    controller = get_controller(mocker)
    controller.call_cls(None)


def test_call_color(mocker):
    controller = get_controller(mocker)
    controller.call_color(None)


def test_call_promptkit(mocker):
    controller = get_controller(mocker)
    controller.call_promptkit(None)


def test_call_predict(mocker):
    controller = get_controller(mocker)
    controller.call_predict(None)


def test_call_thoughts(mocker):
    controller = get_controller(mocker)
    controller.call_thoughts(None)


def test_call_reporthtml(mocker):
    controller = get_controller(mocker)
    controller.call_reporthtml(None)


def test_call_exithelp(mocker):
    controller = get_controller(mocker)
    controller.call_exithelp(None)


def test_call_rcontext(mocker):
    controller = get_controller(mocker)
    controller.call_rcontext(None)


def test_call_dt(mocker):
    controller = get_controller(mocker)
    controller.call_dt(None)


def test_call_rich(mocker):
    controller = get_controller(mocker)
    controller.call_rich(None)


def test_call_richpanel(mocker):
    controller = get_controller(mocker)
    controller.call_richpanel(None)


def test_call_ion(mocker):
    controller = get_controller(mocker)
    controller.call_ion(None)


def test_call_watermark(mocker):
    controller = get_controller(mocker)
    controller.call_watermark(None)


def test_call_cmdloc(mocker):
    controller = get_controller(mocker)
    controller.call_cmdloc(None)


def test_call_autoscaling(mocker):
    controller = get_controller(mocker)
    controller.call_autoscaling(None)


@pytest.mark.parametrize("other", [["45"], ["-v", "45"]])
def test_call_dpi(other, mocker):
    controller = get_controller(mocker)
    controller.call_dpi(other)


@pytest.mark.parametrize("other", [["45"], ["-v", "45"]])
def test_call_height(other, mocker):
    controller = get_controller(mocker)
    controller.call_height(other)


@pytest.mark.parametrize("other", [["45"], ["-v", "45"]])
def test_call_width(other, mocker):
    controller = get_controller(mocker)
    controller.call_width(other)


@pytest.mark.parametrize("other", [["45"], ["-v", "45"]])
def test_call_pheight(other, mocker):
    controller = get_controller(mocker)
    controller.call_pheight(other)


@pytest.mark.parametrize("other", [["45"], ["-v", "45"]])
def test_call_pwidth(other, mocker):
    controller = get_controller(mocker)
    controller.call_pwidth(other)


@pytest.mark.parametrize("other", [["45"], ["-v", "45"]])
def test_call_monitor(other, mocker):
    controller = get_controller(mocker)
    controller.call_monitor(other)


@pytest.mark.parametrize("other", [["GTK3Agg"], ["-v", "GTK3Agg"], ["None"]])
def test_call_backend(other, mocker):
    controller = get_controller(mocker)
    controller.call_backend(other)
