import pytest
from openbb_terminal.econometrics.econometrics_controller import EconometricsController


def get_controller(mocker=None):
    if mocker:
        mocker.patch(
            "openbb_terminal.econometrics.econometrics_controller.obbff.USE_PROMPT_TOOLKIT",
            True,
        )
        mocker.patch(
            "openbb_terminal.econometrics.econometrics_controller.session", True
        )
    return EconometricsController()


def test_update_runtime_choices(mocker):
    controller = get_controller(mocker)
    controller.update_runtime_choices()

    assert controller.choices


@pytest.mark.record_stdout
def test_print_help():
    controller = get_controller()
    controller.print_help()


@pytest.mark.parametrize(
    "other",
    [
        ["-f", "badpath.xlsx"],
        ["-f", "badpath.xlsx", "alias"],
        ["badpath.xlsx"],
        [],
        ["-ex"],
    ],
)
def test_call_load(other):
    controller = get_controller()
    controller.call_load(other)


@pytest.mark.record_stdout
@pytest.mark.parametrize("other", [["data"], ["-n", "data"]])
def test_call_export(other):
    controller = get_controller()
    controller.call_export(other)


@pytest.mark.record_stdout
@pytest.mark.parametrize("other", [["data"], ["-n", "data"], []])
def test_call_remove(other):
    controller = get_controller()
    controller.call_remove(other)


@pytest.mark.parametrize("other", [["data"], ["-n", "data"], []])
def test_call_options(other):
    controller = get_controller()
    controller.call_options(other)


@pytest.mark.skip
@pytest.mark.parametrize("other", [["data"], ["-c", "data"], []])
def test_call_plot(other):
    controller = get_controller()
    controller.call_plot(other)
