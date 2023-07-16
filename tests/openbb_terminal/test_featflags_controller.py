# IMPORTATION STANDARD


# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.core.session.current_user import (
    PreferencesModel,
    copy_user,
)
from openbb_terminal.featflags_controller import FeatureFlagsController

# pylint: disable=W0621


@pytest.fixture()
def controller(mocker):
    preferences = PreferencesModel(USE_PROMPT_TOOLKIT=True)
    mock_current_user = copy_user(preferences=preferences)
    mocker.patch(
        target="openbb_terminal.core.session.current_user.__current_user",
        new=mock_current_user,
    )

    mocker.patch(
        target="openbb_terminal.featflags_controller.set_and_save_preference",
    )

    return FeatureFlagsController()


def test_print_help(controller):
    controller.print_help()


def test_call_cls(controller):
    controller.call_cls(None)


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


def test_call_richpanel(controller):
    controller.call_richpanel(None)
