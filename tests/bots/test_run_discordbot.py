import os

import pytest

# try:
# except ImportError:
#    pytest.skip(allow_module_level=True)


@pytest.fixture(autouse=True)
def change_test_dir(monkeypatch):
    cwd = os.getcwd()
    print(cwd)
    monkeypatch.chdir(cwd + "/bots")
    print(os.getcwd())


@pytest.mark.bots
def test_read_root(mocker, request):
    mocker.patch("bots.run_discordbot.GSTBot", return_value=None)
    cwd = os.getcwd()
    os.chdir(cwd + "/bots")
    from bots import run_discordbot as rdbot

    value = rdbot.read_root()

    assert "Hello" in value
    os.chdir(request.config.invocation_dir)


@pytest.mark.skip
@pytest.mark.bots
def test_hash_user_id(mocker):
    mocker.patch("bots.run_discordbot.gst_bot")
    from bots import run_discordbot as rdbot

    value = rdbot.hash_user_id("Didier")

    assert value
