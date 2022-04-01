import pytest
import telebot


class MockTelegram:
    def set_my_commands(self, commands):
        print(commands)

def test_detect_valid_command(mocker):
    # mocker.patch.object(telebot.TeleBot, MockTelegram())
    mocker.patch("telebot.TeleBot")
    from bots.telegram.run_telegram import detect_valid_command

    assert detect_valid_command("hello") is False
    assert detect_valid_command("ta_ad") is True
