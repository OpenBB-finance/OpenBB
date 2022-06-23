import pytest
from openbb_terminal.portfolio.brokers.coinbase import coinbase_controller


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "queue, expected",
    [
        (["load", "help"], ["help"]),
        (["quit", "help"], ["help"]),
    ],
)
def test_menu_with_queue(expected, mocker, queue):
    path_controller = "openbb_terminal.portfolio.brokers.coinbase.coinbase_controller"

    # MOCK SWITCH
    mocker.patch(
        target=f"{path_controller}.CoinbaseController.switch",
        return_value=["quit"],
    )
    result_menu = coinbase_controller.CoinbaseController(queue=queue).menu()

    assert result_menu == expected


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
            ["quit", "quit", "quit", "reset", "portfolio", "bro", "cb"],
        ),
    ],
)
def test_switch(an_input, expected_queue):
    controller = coinbase_controller.CoinbaseController(queue=None)
    queue = controller.switch(an_input=an_input)

    assert queue == expected_queue
