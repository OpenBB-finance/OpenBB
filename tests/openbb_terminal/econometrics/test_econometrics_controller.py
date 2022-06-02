import pytest
import pandas as pd
from openbb_terminal.econometrics.econometrics_controller import EconometricsController

# pylint: disable=W0621


@pytest.fixture()
def controller(mocker):
    if mocker:
        mocker.patch(
            "openbb_terminal.econometrics.econometrics_controller.obbff.USE_PROMPT_TOOLKIT",
            True,
        )
        mocker.patch(
            "openbb_terminal.econometrics.econometrics_controller.session", True
        )
    return EconometricsController()


def test_update_runtime_choices(controller):
    controller.update_runtime_choices()

    assert controller.choices


@pytest.mark.parametrize(
    "other",
    [
        ["-f", "badpath.xlsx"],
        ["-f", "badpath.xlsx", "alias"],
        ["badpath.xlsx"],
        ["cancer", "dataset"],
        [],
        ["-ex"],
    ],
)
def test_call_load(controller, other):
    controller.call_load(other)


@pytest.mark.parametrize("other", [["dataset"], ["-n", "data"]])
def test_call_export(controller, other):
    controller.call_load(["cancer"])
    controller.call_export(other)


@pytest.mark.skip
@pytest.mark.record_stdout
@pytest.mark.parametrize("other", [["data"], ["-n", "dataset"], []])
def test_call_remove(controller, other):
    controller.call_load(["cancer"])
    controller.call_remove(other)


@pytest.mark.skip
@pytest.mark.parametrize("other", [["data"], ["-n", "data"], []])
def test_call_options(controller, other):
    controller.call_options(other)


@pytest.mark.parametrize("other", [["cancer-dataset"], ["-c", "data"], []])
def test_call_plot(controller, other):
    controller.call_load(["cancer", "dataset"])
    controller.call_plot(other)


@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "other",
    [
        ["data"],
        ["-n", "dataset", "-s", "badcol"],
        ["-n", "dataset", "-s", "cancer"],
        [],
    ],
)
def test_call_show(controller, other):
    controller.call_load(["cancer", "dataset"])
    controller.call_show(other)
    controller.datasets = {"dataset": pd.DataFrame()}
    controller.call_show(["dataset"])


@pytest.mark.record_stdout
@pytest.mark.parametrize("other", [["data"], ["-n", "dataset"], []])
def test_call_desc(controller, other):
    controller.call_load(["cancer", "dataset"])
    controller.call_desc(other)
    controller.datasets = {"dataset": pd.DataFrame()}
    controller.call_desc(["dataset"])


@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "other",
    [
        ["data"],
        ["-n", "dataset"],
        [],
        ["cancer-dataset", "int"],
        ["cancer-dataset", "badbad"],
        ["cancer-dataset", "date"],
    ],
)
def test_call_type(controller, other):
    controller.call_load(["cancer", "dataset"])
    controller.call_type(other)


@pytest.mark.record_stdout
def test_call_index(controller):
    controller.call_load(["cancer", "dataset"])
    controller.call_index(["dataset", "cancer", "-a"])
    controller.call_index(["dataset", "cancer", "-a"])
    controller.call_index(["dataset", "cancer", "-d"])
    controller.call_index(["dataset", "cancer", "oogabooga", "-d"])


@pytest.mark.record_stdout
@pytest.mark.parametrize("other", [["data"], ["-n", "dataset"], []])
def test_call_ols(controller, other):
    controller.call_load(["cancer", "dataset"])
    controller.call_ols(other)


@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "other", [["cancer-dataset"], ["cancer-datast"], ["-n", "dataset"], []]
)
def test_call_norm(controller, other):
    controller.call_load(["cancer", "dataset"])
    controller.call_norm(other)


@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "other", [["cancer-dataset"], ["cancer-datast"], ["-n", "dataset"], []]
)
def test_call_root(controller, other):
    controller.call_load(["cancer", "dataset"])
    controller.call_root(other)


@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "other",
    [
        ["cancer-dataset"],
        ["-r", "cancer-dataset", "population-dataset", "-t", "pols", "-ee", "-te"],
    ],
)
def test_call_panel(controller, other):
    controller.call_load(["cancer", "dataset"])
    controller.call_panel(other)


@pytest.mark.record_stdout
def test_call_compare(controller):
    controller.call_load(["cancer", "dataset"])
    controller.call_compare([])


@pytest.mark.record_stdout
@pytest.mark.parametrize("other", [["data"], ["-n", "dataset"], []])
def test_call_dwat(controller, other):
    controller.call_load(["cancer", "dataset"])
    controller.call_dwat(other)


@pytest.mark.record_stdout
@pytest.mark.parametrize("other", [["data"], ["-n", "dataset"], []])
def test_call_bgod(controller, other):
    controller.call_load(["cancer", "dataset"])
    controller.call_bgod(other)


@pytest.mark.record_stdout
@pytest.mark.parametrize("other", [["data"], ["-n", "dataset"], []])
def test_call_bpag(controller, other):
    controller.call_load(["cancer", "dataset"])
    controller.call_bpag(other)


@pytest.mark.record_stdout
@pytest.mark.parametrize("other", [["data"], ["-n", "dataset"], []])
def test_call_granger(controller, other):
    controller.call_load(["cancer", "dataset"])
    controller.call_granger(other)


@pytest.mark.record_stdout
@pytest.mark.parametrize("other", [["data"], ["-n", "dataset"], []])
def test_call_coint(controller, other):
    controller.call_load(["cancer", "dataset"])
    controller.call_coint(other)
