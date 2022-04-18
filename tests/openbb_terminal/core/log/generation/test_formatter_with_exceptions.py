import os
import pytest
from openbb_terminal.core.log.generation import formatter_with_exceptions as fwe
from openbb_terminal.core.log.generation.settings import AppSettings
from openbb_terminal.core.config.constants import REPO_DIR

app_settings = AppSettings(
    commit_hash="MOCK_COMMIT_HASH",
    name="MOCK_COMMIT_HASH",
    identifier="MOCK_COMMIT_HASH",
    session_id="MOCK_SESSION_ID",
)


class Record:
    def __init__(self, exc_text, levelname):
        self.exc_text = exc_text
        self.levelname = levelname
        self.func_name_override = "Hello"
        self.session_id = 6
        self.created = True
        self.name = "Name"
        self.exc_info = "hello"
        self.stack_info = "stack"

    def getMessage(self):
        return "a really cool message"


formatter = fwe.FormatterWithExceptions(app_settings)


@pytest.mark.parametrize("exc, level", [(True, True), (False, "name"), (False, False)])
def test_calculate_level_name(exc, level):
    value = formatter.calculate_level_name(Record(exc, level))
    assert value


def test_extract_log_extra():
    value = formatter.extract_log_extra(Record(True, "name"))
    assert value


def test_filter_piis():
    text = f"test 1.1.1.1 chavi@chavi.com {REPO_DIR.name}{os.sep} dd{os.sep}dd"
    value = formatter.filter_piis(text)
    assert value


def test_filter_special_characters():
    text = "\nhello \this \rgreetings"
    value = formatter.filter_special_characters(text)
    assert value == " - hello  his greetings"


def test_detect_terminal_message():
    value = formatter.detect_terminal_message("The command doesn't exist on the")
    assert value
    new_val = formatter.detect_terminal_message("boring message")
    assert not new_val


def test_filter_log_line():
    value = formatter.filter_log_line("stocks")
    assert value
    value = formatter.filter_log_line(
        "The command doesn't exist on the menu. - Traceback hello"
    )
    assert value


def test_formatException():
    with pytest.raises(Exception):
        formatter.formatException(Exception("Big bad error"))


def test_format():
    value = formatter.format(Record("Text", ""))
    assert value
