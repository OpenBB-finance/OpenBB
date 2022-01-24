import os
import pytest
import pandas as pd
from gamestonk_terminal.custom import custom_controller


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_print_help():
    controller = custom_controller.CustomDataController()
    controller.print_help()


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_info_no_data():
    controller = custom_controller.CustomDataController()
    controller.choices = []
    controller.data = pd.DataFrame()
    controller.call_info([])


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "queue, expected",
    [
        (["load", "help"], []),
        (["quit", "help"], ["help"]),
    ],
)
def test_menu_with_queue(expected, mocker, queue):
    path_controller = "gamestonk_terminal.custom.custom_controller"

    # MOCK SWITCH
    mocker.patch(
        target=f"{path_controller}.CustomDataController.switch",
        return_value=["quit"],
    )
    result_menu = custom_controller.CustomDataController(queue=queue).menu()

    assert result_menu == expected


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "tested_func, other_args, mocked_func, called_args, called_kwargs",
    [
        (
            "call_load",
            [
                "-f test.csv",
            ],
            "",
            [],
            dict(),
        ),
    ],
)
def test_call_func_test(
    tested_func, mocked_func, other_args, called_args, called_kwargs, mocker
):
    path_controller = "gamestonk_terminal.custom.custom_controller"

    if mocked_func:
        mock = mocker.Mock()
        mocker.patch(
            target=f"{path_controller}.{mocked_func}",
            new=mock,
        )

        controller = custom_controller.CustomDataController(queue=None)
        getattr(controller, tested_func)(other_args)

        if called_args or called_kwargs:
            mock.assert_called_once_with(*called_args, **called_kwargs)
        else:
            mock.assert_called_once()
    else:
        controller = custom_controller.CustomDataController(queue=None)
        getattr(controller, tested_func)(other_args)


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "tested_func, other_args, mocked_func, called_args, called_kwargs",
    [
        (
            "call_show",
            [
                "-l 2",
            ],
            "",
            [],
            dict(),
        ),
    ],
)
def test_controller_show(
    tested_func, mocked_func, other_args, called_args, called_kwargs, mocker
):
    path_controller = "gamestonk_terminal.custom.custom_controller"

    if mocked_func:
        mock = mocker.Mock()
        mocker.patch(
            target=f"{path_controller}.{mocked_func}",
            new=mock,
        )

        controller = custom_controller.CustomDataController(queue=None)
        controller.data = pd.read_csv(os.path.join("custom_imports", "test.csv"))
        getattr(controller, tested_func)(other_args)

        if called_args or called_kwargs:
            mock.assert_called_once_with(*called_args, **called_kwargs)
        else:
            mock.assert_called_once()
    else:
        controller = custom_controller.CustomDataController(queue=None)
        getattr(controller, tested_func)(other_args)
