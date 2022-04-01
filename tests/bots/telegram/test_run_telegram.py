import pytest
import telebot


class MockTelegram:
    def set_my_commands(self, commands):
        print(commands)


@pytest.mark.record_stdout
def test_detect_valid_command(mocker):
    mocker.patch("bots.telegram.run_telegram.telebot")
    from bots.telegram.run_telegram import detect_valid_command

    assert detect_valid_command("hello") is False
    assert detect_valid_command("ta_ad") is True
