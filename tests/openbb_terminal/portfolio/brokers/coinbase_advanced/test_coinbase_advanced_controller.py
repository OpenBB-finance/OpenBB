import pytest
from openbb_terminal.portfolio.brokers.coinbase_advanced import (
    coinbase_advanced_controller,
)


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "queue, expected",
    [
        (["load", "help"], ["help"]),
        (["quit", "help"], ["help"]),
    ],
)
def test_menu_with_queue(expected, mocker, queue):
    path_controller = "openbb_terminal.portfolio.brokers.coinbase_advanced.coinbase_advanced_controller"

    # MOCK SWITCH
    mocker.patch(
        target=f"{path_controller}.CoinbaseAdvController.switch",
        return_value=["quit"],
    )
    result_menu = coinbase_advanced_controller.CoinbaseAdvController(queue=queue).menu()

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
            ["quit", "quit", "quit", "reset", "portfolio", "bro", "cbadv"],
        ),
    ],
)
def test_switch(an_input, expected_queue):
    controller = coinbase_advanced_controller.CoinbaseAdvController(queue=None)
    queue = controller.switch(an_input=an_input)

    assert queue == expected_queue
