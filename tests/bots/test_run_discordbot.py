import sys
from pathlib import Path

import pytest

try:
    from bots import run_discordbot as rdbot
except ImportError:
    sys.path.append(str(Path(__file__).parent.resolve().__str__))
    from bots import run_discordbot as rdbot

# try:
# except ImportError:
#    pytest.skip(allow_module_level=True)


@pytest.mark.bots
def test_read_root(mocker):
    mocker.patch("bots.run_discordbot.gst_bot")

    value = rdbot.read_root()

    assert "Hello" in value


@pytest.mark.bots
def test_hash_user_id(mocker):
    mocker.patch("bots.run_discordbot.gst_bot")

    value = rdbot.hash_user_id("Didier")

    assert value
