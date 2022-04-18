from pathlib import Path
from openbb_terminal.core.log.collection import log_sender
from openbb_terminal.core.log.generation.settings import (
    Settings,
    AppSettings,
    AWSSettings,
    LogSettings,
)

settings = Settings(
    app_settings=AppSettings(
        commit_hash="MOCK_COMMIT_HASH",
        name="MOCK_COMMIT_HASH",
        identifier="MOCK_COMMIT_HASH",
        session_id="MOCK_SESSION_ID",
    ),
    aws_settings=AWSSettings(
        aws_access_key_id="MOCK_AWS_ACCESS_KEY_ID",
        aws_secret_access_key="MOCK_AWS",  # pragma: allowlist secret
    ),
    log_settings=LogSettings(
        directory=Path("."),
        frequency="H",
        handler_list="file",
        rolling_clock=False,
        verbosity=20,
    ),
)


def test_queue_str():
    log_sender.QueueItem(Path(".")).__str__()


def test_sender_settings():
    value = log_sender.LogSender(settings).settings
    assert value is not None


def test_sender_fails():
    value = log_sender.LogSender(settings).fails
    assert value is not None


def test_sender_queue():
    value = log_sender.LogSender(settings).queue
    assert value is not None
