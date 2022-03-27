import pytest


class MockTelegram:
    def set_my_commands(self, commands):
        print(commands)


# TODO: Ask Chavi for help
@pytest.mark.skip
@pytest.mark.record_stdout
def test_detect_valid_command(mocker):
    # mocker.patch.object(telebot.TeleBot, MockTelegram())
    mocker.patch(
        "bots.telegram.run_telegram.telebot.set_my_commands", return_value=True
    )
    from bots.telegram.run_telegram import detect_valid_command

    assert detect_valid_command("hello") is False
    assert detect_valid_command("ta_ad") is True
