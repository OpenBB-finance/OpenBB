# IMPORTATION STANDARD
import dataclasses

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.core.models.preferences_model import PreferencesModel
from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.featflags_controller import FeatureFlagsController

# pylint: disable=W0621


@pytest.fixture()
def controller(mocker):
    current_user = get_current_user()
    preference = PreferencesModel(USE_PROMPT_TOOLKIT=True)
    user_model = dataclasses.replace(current_user, preference=preference)
    mocker.patch(
        target="openbb_terminal.core.session.current_user.get_current_user",
        return_value=user_model,
    )

    mocker.patch(
        target="openbb_terminal.featflags_controller.set_preference",
    )

    mocker.patch(target="openbb_terminal.core.session.preferences_handler.set_preference")
    return FeatureFlagsController()


def test_print_help(controller):
    controller.print_help()


def test_call_tab(controller):
    controller.call_tab(None)


def test_call_cls(controller):
    controller.call_cls(None)


def test_call_color(controller):
    controller.call_color(None)


def test_call_promptkit(controller):
    controller.call_promptkit(None)


def test_call_thoughts(controller):
    controller.call_thoughts(None)


def test_call_reporthtml(controller):
    controller.call_reporthtml(None)


def test_call_exithelp(controller):
    controller.call_exithelp(None)


def test_call_rcontext(controller):
    controller.call_rcontext(None)


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
