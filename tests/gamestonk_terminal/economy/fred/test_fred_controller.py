# IMPORTATION STANDARD
import os
from datetime import datetime

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.economy.fred import fred_controller

# pylint: disable=E1101
# pylint: disable=W0603
# pylint: disable=E1111


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "queue, expected",
    [
        (["load", "help"], []),
        (["quit", "help"], ["help"]),
    ],
)
def test_menu_with_queue(expected, mocker, queue):
    path_controller = "gamestonk_terminal.economy.fred.fred_controller"

    # MOCK SWITCH
    mocker.patch(
        target=f"{path_controller}.FredController.switch",
        return_value=["quit"],
    )
    result_menu = fred_controller.FredController(queue=queue).menu()

    assert result_menu == expected


@pytest.mark.vcr(record_mode="none")
def test_menu_without_queue_completion(mocker):
    path_controller = "gamestonk_terminal.economy.fred.fred_controller"

    # ENABLE AUTO-COMPLETION : HELPER_FUNCS.MENU
    mocker.patch(
        target="gamestonk_terminal.feature_flags.USE_PROMPT_TOOLKIT",
        new=True,
    )
    mocker.patch(
        target="gamestonk_terminal.parent_classes.session",
    )
    mocker.patch(
        target="gamestonk_terminal.parent_classes.session.prompt",
        return_value="quit",
    )

    # DISABLE AUTO-COMPLETION : CONTROLLER.COMPLETER
    mocker.patch.object(
        target=fred_controller.gtff,
        attribute="USE_PROMPT_TOOLKIT",
        new=True,
    )
    mocker.patch(
        target=f"{path_controller}.session",
    )
    mocker.patch(
        target=f"{path_controller}.session.prompt",
        return_value="quit",
    )

    result_menu = fred_controller.FredController(queue=None).menu()

    assert result_menu == []


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "mock_input",
    ["help", "homee help", "home help", "mock"],
)
def test_menu_without_queue_sys_exit(mock_input, mocker):
    path_controller = "gamestonk_terminal.economy.fred.fred_controller"

    # DISABLE AUTO-COMPLETION
    mocker.patch.object(
        target=fred_controller.gtff,
        attribute="USE_PROMPT_TOOLKIT",
        new=False,
    )
    mocker.patch(
        target=f"{path_controller}.session",
        return_value=None,
    )

    # MOCK USER INPUT
    mocker.patch("builtins.input", return_value=mock_input)

    # MOCK SWITCH
    class SystemExitSideEffect:
        def __init__(self):
            self.first_call = True

        def __call__(self, *args, **kwargs):
            if self.first_call:
                self.first_call = False
                raise SystemExit()
            return ["quit"]

    mock_switch = mocker.Mock(side_effect=SystemExitSideEffect())
    mocker.patch(
        target=f"{path_controller}.FredController.switch",
        new=mock_switch,
    )

    result_menu = fred_controller.FredController(queue=None).menu()

    assert result_menu == []


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_print_help():
    controller = fred_controller.FredController(queue=None)
    controller.long_id = len("MOCK_SERIES_ID_1")
    controller.current_series["MOCK_SERIES_ID_1"] = {
        "title": "MOCK_TITLE_11",
        "units_short": "MOCK_UNITS_SHORT_11",
    }
    controller.current_series["MOCK_SERIES_ID_2"] = {
        "title": "MOCK_TITLE_21",
        "units_short": "MOCK_UNITS_SHORT_21",
    }
    controller.print_help()


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "an_input, expected_queue",
    [
        ("", []),
        ("/help", ["home", "help"]),
        ("help/help", ["help", "help"]),
        ("q", ["quit"]),
        ("h", []),
        (
            "r",
            [
                "quit",
                "quit",
                "reset",
                "economy",
                "fred",
            ],
        ),
    ],
)
def test_switch(an_input, expected_queue):
    controller = fred_controller.FredController(queue=None)
    queue = controller.switch(an_input=an_input)

    assert queue == expected_queue


@pytest.mark.vcr(record_mode="none")
def test_call_cls(mocker):
    mocker.patch("os.system")

    controller = fred_controller.FredController(queue=None)
    controller.call_cls([])

    assert controller.queue == []
    os.system.assert_called_once_with("cls||clear")


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "func, queue, expected_queue",
    [
        (
            "call_exit",
            [],
            ["quit", "quit", "quit"],
        ),
        ("call_exit", ["help"], ["quit", "quit", "quit", "help"]),
        ("call_home", [], ["quit", "quit"]),
        ("call_help", [], []),
        ("call_quit", [], ["quit"]),
        ("call_quit", ["help"], ["quit", "help"]),
        (
            "call_reset",
            [],
            [
                "quit",
                "quit",
                "reset",
                "economy",
                "fred",
            ],
        ),
        (
            "call_reset",
            ["help"],
            [
                "quit",
                "quit",
                "reset",
                "economy",
                "fred",
                "help",
            ],
        ),
    ],
)
def test_call_func_expect_queue(expected_queue, func, queue):
    controller = fred_controller.FredController(queue=queue)
    result = getattr(controller, func)([])

    assert result is None
    assert controller.queue == expected_queue


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "tested_func, other_args, mocked_func, called_args, called_kwargs",
    [
        (
            "call_search",
            [
                "MOCK_SERIES",
                "--num=1",
            ],
            "fred_view.notes",
            [],
            dict(
                series_term="MOCK_SERIES",
                num=1,
            ),
        ),
        (
            "call_rmv",
            [
                "MOCK_DICT_KEY_1",
            ],
            "",
            [],
            dict(),
        ),
        (
            "call_plot",
            ["MOCK_SERIES_ID", "-s=2021-01-01", "--raw", "--lim=1", "--export=csv"],
            "fred_view.display_fred_series",
            [
                {"MOCK_DICT_KEY_1": "MOCK_DICT_VALUE_1"},
                datetime.strptime("2021-01-01", "%Y-%m-%d"),
                True,
                "csv",
                1,
            ],
            dict(),
        ),
    ],
)
def test_call_func(
    tested_func, mocked_func, other_args, called_args, called_kwargs, mocker
):
    path_controller = "gamestonk_terminal.economy.fred.fred_controller"

    if mocked_func:
        mock = mocker.Mock()
        mocker.patch(
            target=f"{path_controller}.{mocked_func}",
            new=mock,
        )

        controller = fred_controller.FredController(queue=None)
        controller.current_series = {"MOCK_DICT_KEY_1": "MOCK_DICT_VALUE_1"}

        getattr(controller, tested_func)(other_args)

        if called_args or called_kwargs:
            mock.assert_called_once_with(*called_args, **called_kwargs)
        else:
            mock.assert_called_once()
    else:
        controller = fred_controller.FredController(queue=None)
        controller.current_series = {"MOCK_DICT_KEY_1": "MOCK_DICT_VALUE_1"}

        getattr(controller, tested_func)(other_args)


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_call_add(mocker):
    path_controller = "gamestonk_terminal.economy.fred.fred_controller"

    # MOCK CHECK_SERIES_ID
    mock_exists = True
    mock_information = {
        "seriess": [
            {"title": "MOCK_TITLE_1", "units_short": "MOCK_UNITS_SHORT_1"},
        ]
    }
    mocker.patch(
        target=f"{path_controller}.fred_model.check_series_id",
        return_value=(mock_exists, mock_information),
    )

    controller = fred_controller.FredController(queue=None)
    other_args = [
        "MOCK_SERIES_ID",
    ]
    controller.call_add(other_args=other_args)


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_call_add_not_found(mocker):
    path_controller = "gamestonk_terminal.economy.fred.fred_controller"

    # MOCK CHECK_SERIES_ID
    mock_exists = False
    mock_information = {
        "seriess": [
            {"title": "MOCK_TITLE_1", "units_short": "MOCK_UNITS_SHORT_1"},
        ]
    }
    mocker.patch(
        target=f"{path_controller}.fred_model.check_series_id",
        return_value=(mock_exists, mock_information),
    )

    controller = fred_controller.FredController(queue=None)
    other_args = [
        "MOCK_SERIES_ID",
    ]
    controller.call_add(other_args=other_args)


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "current_series",
    [
        {},
        {
            "MOCK_DICT_KEY_1": "MOCK_DICT_VALUE_1",
            "MOCK_DICT_KEY_2": "MOCK_DICT_VALUE_2",
        },
    ],
)
def test_call_pred(current_series):
    controller = fred_controller.FredController(queue=None)
    controller.current_series = current_series

    controller.call_pred([])
