import pytest

# pylint: disable=C0415


@pytest.mark.bots
def test_read_root(mocker):
    mocker.patch("bots.run_discordbot.gst_bot")
    from bots import run_discordbot as rdbot

    value = rdbot.read_root()

    assert "Hello" in value


@pytest.mark.bots
def test_hash_user_id(mocker):
    mocker.patch("bots.run_discordbot.gst_bot")
    from bots import run_discordbot as rdbot

    value = rdbot.hash_user_id("Didier")

    assert value
