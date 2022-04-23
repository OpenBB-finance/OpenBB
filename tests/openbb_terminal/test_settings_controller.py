import pytest

from openbb_terminal.settings_controller import SettingsController

# pylint: disable=W0621


@pytest.fixture()
def controller(mocker):
    mocker.patch(
        "openbb_terminal.settings_controller.obbff.USE_PROMPT_TOOLKIT",
        True,
    )
    mocker.patch("openbb_terminal.settings_controller.session", True)
    mocker.patch("openbb_terminal.settings_controller.set_key")
    mocker.patch("openbb_terminal.settings_controller.obbff")
    return SettingsController()


def test_print_help(controller):
    controller.print_help()


def test_call_logcollection(controller):
    controller.call_logcollection(None)


def test_call_tab(controller):
    controller.call_tab(None)


def test_call_cls(controller):
    controller.call_cls(None)


def test_call_color(controller):
    controller.call_color(None)


def test_call_promptkit(controller):
    controller.call_promptkit(None)


def test_call_predict(controller):
    controller.call_predict(None)


def test_call_thoughts(controller):
    controller.call_thoughts(None)


def test_call_reporthtml(controller):
    controller.call_reporthtml(None)


def test_call_exithelp(controller):
    controller.call_exithelp(None)


def test_call_rcontext(controller):
    controller.call_rcontext(None)


def test_call_dt(controller):
    controller.call_dt(None)


def test_call_rich(controller):
    controller.call_rich(None)


def test_call_richpanel(controller):
    controller.call_richpanel(None)


def test_call_ion(controller):
    controller.call_ion(None)


def test_call_watermark(controller):
    controller.call_watermark(None)


def test_call_cmdloc(controller):
    controller.call_cmdloc(None)


def test_call_autoscaling(controller):
    controller.call_autoscaling(None)


@pytest.mark.parametrize("other", [["45"], ["-v", "45"]])
def test_call_dpi(controller, other):
    controller.call_dpi(other)


@pytest.mark.parametrize("other", [["45"], ["-v", "45"]])
def test_call_height(controller, other):
    controller.call_height(other)


@pytest.mark.parametrize("other", [["45"], ["-v", "45"]])
def test_call_width(controller, other):
    controller.call_width(other)


@pytest.mark.parametrize("other", [["45"], ["-v", "45"]])
def test_call_pheight(controller, other):
    controller.call_pheight(other)


@pytest.mark.parametrize("other", [["45"], ["-v", "45"]])
def test_call_pwidth(controller, other):
    controller.call_pwidth(other)


@pytest.mark.parametrize("other", [["45"], ["-v", "45"]])
def test_call_monitor(controller, other):
    controller.call_monitor(other)


@pytest.mark.parametrize("other", [["GTK3Agg"], ["-v", "GTK3Agg"], ["None"]])
def test_call_backend(controller, other):
    controller.call_backend(other)
