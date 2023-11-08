# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.core.log.generation.formatter_with_exceptions import (
    FormatterWithExceptions,
)
from openbb_terminal.core.log.generation.settings import AppSettings

app_settings = AppSettings(
    commit_hash="MOCK_COMMIT_HASH",
    name="MOCK_COMMIT_HASH",
    identifier="MOCK_COMMIT_HASH",
    session_id="MOCK_SESSION_ID",
    user_id="MOCK_USER_ID",
)
formatter = FormatterWithExceptions(app_settings)


@pytest.mark.parametrize("exc, level", [(True, True), (False, "name"), (False, False)])
def test_calculate_level_name(exc, level, mocker, recorder):
    mock = mocker.Mock()
    mock.exc_text = exc
    mock.levelname = level
    text_expected = FormatterWithExceptions.calculate_level_name(mock)
    recorder.capture(text_expected)


def test_extract_log_extra(mocker, recorder):
    mock = mocker.Mock()
    mock.exc_text = True
    mock.levelname = "MOCK_LEVELNAME"
    mock.user_id = "MOCK_USER_ID"
    mock.session_id = "MOCK_SESSION_ID"
    text_expected = FormatterWithExceptions.extract_log_extra(mock)
    recorder.capture(text_expected)


def test_filter_log_line(recorder):
    text = "test 1.1.1.1 testestest chavi@chavi.com testestest C:\\Users\\username\\some folder\\some path testestest"
    text_expected = FormatterWithExceptions.filter_log_line(text=text)
    recorder.capture(text_expected)

    text = "test 1.1.1.1 testestest chavi@chavi.com testestest /home/username/some folder/some path testestest"
    text_expected = FormatterWithExceptions.filter_log_line(text=text)
    recorder.capture(text_expected)

    text = "\nhello this is greetings"
    text_expected = FormatterWithExceptions.filter_log_line(text=text)
    recorder.capture(text_expected)


def test_formatException_invalid():
    with pytest.raises(Exception):
        formatter.formatException(Exception("Big bad error"))


def test_format(mocker):
    mock = mocker.Mock()
    mock.exc_text = "Text"
    mock.levelname = ""
    mock.created = 6
    mock.name = "Hello"
    mock.getMessage = lambda: "aeffew"
    mock.stack_info = "info"
    value = formatter.format(mock)
    assert value
