import pytest
from openbb_terminal.core.log.collection import log_sender
from openbb_terminal.core.log.generation.settings import (
    Settings,
    AppSettings,
    AWSSettings,
    LogSettings,
)


@pytest.fixture(name="settings")
def fixture_settings(tmp_path):
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
            directory=tmp_path,
            frequency="H",
            handler_list="file",
            rolling_clock=False,
            verbosity=20,
        ),
    )
    return settings


def test_queue_str(tmp_path):
    log_sender.QueueItem(tmp_path).__str__()


def test_sender_settings(settings):
    value = log_sender.LogSender(settings).settings
    assert value is not None


def test_sender_fails(settings):
    value = log_sender.LogSender(settings).fails
    assert value is not None


def test_sender_queue(settings):
    value = log_sender.LogSender(settings).queue
    assert value is not None
