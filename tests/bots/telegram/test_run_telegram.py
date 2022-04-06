import pytest


class MockMessage:
    def __init__(self, text):
        self.text = text


@pytest.mark.bots
def test_detect_valid_command(mocker):
    mocker.patch("telebot.TeleBot")
    from bots.telegram.run_telegram import detect_valid_command

    assert detect_valid_command(MockMessage("/hello")) is False
    assert detect_valid_command(MockMessage("/ta_ad")) is True


@pytest.mark.bots
def test_send_welcome(mocker):
    mocker.patch("telebot.TeleBot")
    from bots.telegram.run_telegram import send_welcome

    send_welcome(MockMessage("/hello"))


@pytest.mark.bots
def test_send_cmds(mocker):
    mocker.patch("telebot.TeleBot")
    from bots.telegram.run_telegram import send_cmds

    send_cmds(MockMessage("/hello"))


@pytest.mark.bots
def test_send_command(mocker):
    mocker.patch("telebot.TeleBot")
    from bots.telegram.run_telegram import send_command

    send_command(MockMessage("/hello"))
