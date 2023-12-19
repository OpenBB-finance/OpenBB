from openbb_terminal.core.log.generation.settings import (
    AppSettings,
    AWSSettings,
    LogSettings,
    Settings,
)


def test_aws_settings():
    aws_access_key_id = "MOCK_AWS_ACCESS_KEY_ID"
    aws_secret_access_key = "MOCK_AWS_SECRET_ACCESS_KEY"  # noqa: S105

    aws_settings = AWSSettings(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )

    assert aws_settings.aws_access_key_id == aws_access_key_id
    assert aws_settings.aws_secret_access_key == aws_secret_access_key


def test_app_settings():
    name = "MOCK_NAME"
    commit_hash = "MOCK_COMMIT_HASH"
    session_id = "MOCK_SESSION_ID"
    identifier = "MOCK_IDENTIFIER"
    user_id = "MOCK_USER_ID"

    app_settings = AppSettings(
        name=name,
        commit_hash=commit_hash,
        session_id=session_id,
        identifier=identifier,
        user_id=user_id,
    )

    assert app_settings.name == name
    assert app_settings.commit_hash == commit_hash
    assert app_settings.session_id == session_id
    assert app_settings.identifier == identifier


def test_log_settings(tmp_path):
    directory = tmp_path
    frequency = "MOCK_FREQUENCY"
    handler_list = ["MOCK_HANDLER_LIST"]
    rolling_clock = "MOCK_ROLLING_CLOCK"
    verbosity = 20

    log_settings = LogSettings(
        directory=directory,
        frequency=frequency,
        handler_list=handler_list,
        rolling_clock=rolling_clock,
        verbosity=verbosity,
    )

    assert log_settings.directory == directory
    assert log_settings.frequency == frequency
    assert log_settings.handler_list == handler_list
    assert log_settings.rolling_clock == rolling_clock
    assert log_settings.verbosity == verbosity


def test_settings(tmp_path):
    directory = tmp_path
    frequency = "MOCK_FREQUENCY"
    handler_list = ["MOCK_HANDLER_LIST"]
    rolling_clock = "MOCK_ROLLING_CLOCK"
    verbosity = 20
    log_settings = LogSettings(
        directory=directory,
        frequency=frequency,
        handler_list=handler_list,
        rolling_clock=rolling_clock,
        verbosity=verbosity,
    )

    name = "MOCK_NAME"
    commit_hash = "MOCK_COMMIT_HASH"
    session_id = "MOCK_SESSION_ID"
    identifier = "MOCK_IDENTIFIER"
    user_id = "MOCK_USER_ID"
    app_settings = AppSettings(
        name=name,
        commit_hash=commit_hash,
        session_id=session_id,
        identifier=identifier,
        user_id=user_id,
    )

    aws_access_key_id = "MOCK_AWS_ACCESS_KEY_ID"
    aws_secret_access_key = "MOCK_AWS_SECRET_ACCESS_KEY"  # noqa: S105
    aws_settings = AWSSettings(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )

    settings = Settings(
        app_settings=app_settings,
        aws_settings=aws_settings,
        log_settings=log_settings,
    )

    assert settings.app_settings != app_settings
    assert settings.aws_settings != aws_settings
    assert settings.log_settings != log_settings

    assert isinstance(settings.app_settings, AppSettings)
    assert isinstance(settings.aws_settings, AWSSettings)
    assert isinstance(settings.log_settings, LogSettings)
