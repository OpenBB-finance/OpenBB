import pytest
from openbb_terminal.core.log.generation.settings import (
    Settings,
    AppSettings,
    AWSSettings,
    LogSettings,
)


@pytest.fixture()
def settings(tmp_path):
    settings_obj = Settings(
        app_settings=AppSettings(
            commit_hash="MOCK_COMMIT_HASH",
            name="MOCK_NAME",
            identifier="MOCK_IDENTIFIER",
            session_id="MOCK_SESSION_ID",
        ),
        aws_settings=AWSSettings(
            aws_access_key_id="MOCK_AWS_ACCESS_KEY_ID",
            aws_secret_access_key="MOCK_AWS_ACCESS_KEY",  # pragma: allowlist secret
        ),
        log_settings=LogSettings(
            directory=tmp_path,
            frequency="H",
            handler_list="file",
            rolling_clock=False,
            verbosity=20,
        ),
    )
    return settings_obj
