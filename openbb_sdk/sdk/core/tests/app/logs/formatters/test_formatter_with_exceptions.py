import logging
import os
from unittest.mock import Mock

import pytest
from openbb_core.app.logs.formatters.formatter_with_exceptions import (
    FormatterWithExceptions,
)

logging_settings = Mock()
logging_settings.app_name = "test_app_name"
logging_settings.app_id = "test_app_id"
logging_settings.session_id = "test_session_id"
logging_settings.user_id = "test_user_id"


@pytest.fixture
def formatter():
    return FormatterWithExceptions(logging_settings)


# Test when exc_text is not empty (should return "X")
def test_level_name_with_exc_text(formatter):
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="",
        args=None,
        exc_info=None,
        func=None,
    )
    record.exc_text = "Exception occurred!"
    assert formatter.calculate_level_name(record) == "X"


# Test when levelname is not empty (should return the first character of levelname)
def test_level_name_with_levelname(formatter):
    record = logging.LogRecord(
        name="test_logger",
        level=logging.WARNING,
        pathname="",
        lineno=0,
        msg="",
        args=None,
        exc_info=None,
        func=None,
    )
    record.levelname = "WARNING"
    assert formatter.calculate_level_name(record) == "W"


# Test when func_name_override and session_id are present in the record
def test_extract_log_extra_with_override_and_session_id(formatter):
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="",
        args=None,
        exc_info=None,
        func=None,
    )
    record.func_name_override = "custom_function"
    record.session_id = "1234567890"

    log_extra = formatter.extract_log_extra(record)

    assert log_extra == {
        "sessionId": "1234567890",
    }


# Test when only func_name_override is present in the record
def test_extract_log_extra_with_override(formatter):
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="",
        args=None,
        exc_info=None,
        func=None,
    )
    record.func_name_override = "custom_function"

    log_extra = formatter.extract_log_extra(record)

    assert log_extra == {}
    assert record.funcName == "custom_function"
    assert record.lineno == 0


# Test when only session_id is present in the record
def test_extract_log_extra_with_session_id(formatter):
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="",
        args=None,
        exc_info=None,
        func=None,
    )
    record.session_id = "1234567890"

    log_extra = formatter.extract_log_extra(record)

    assert log_extra == {
        "sessionId": "1234567890",
    }


# Test when neither func_name_override nor session_id are present in the record
def test_extract_log_extra_with_no_override_or_session_id(formatter):
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="",
        args=None,
        exc_info=None,
        func=None,
    )

    log_extra = formatter.extract_log_extra(record)

    assert log_extra == {}


@pytest.mark.parametrize(
    "input_text, expected_output",
    [
        ("Hello, this is 192.168.1.1", "Hello, this is  FILTERED_IP "),
        ("IP address: 10.0.0.1", "IP address:  FILTERED_IP "),
        ("No IPs here!", "No IPs here!"),
        ("Another IP: 172.16.32.1", "Another IP:  FILTERED_IP "),
        ("1.2.3.4", " FILTERED_IP "),
    ],
)
def test_mock_ipv4(input_text, expected_output, formatter):
    assert formatter.mock_ipv4(input_text) == expected_output


@pytest.mark.parametrize(
    "input_text, expected_output",
    [
        ("Send an email to john@example.com", "Send an email to  FILTERED_EMAIL "),
        ("No emails here!", "No emails here!"),
        ("Another email: alice@example.co.uk", "Another email:  FILTERED_EMAIL "),
        ("Contact us: support@example.net", "Contact us:  FILTERED_EMAIL "),
        ("myemail@example.com 12345", " FILTERED_EMAIL  12345"),
    ],
)
def test_mock_email(input_text, expected_output, formatter):
    assert formatter.mock_email(input_text) == expected_output


@pytest.mark.parametrize(
    "input_text, expected_output",
    [
        ('{"password": "secure_pass_123"}', '{"password": " FILTERED_PASSWORD "}'),
        ('{"password": "p@$$w0rd!"}', '{"password": " FILTERED_PASSWORD "}'),
        ('{"password": "12345"}', '{"password": " FILTERED_PASSWORD "}'),
        ('{"password": "abc"}', '{"password": " FILTERED_PASSWORD "}'),
        (
            '{"password": "my_password"} {"password": "test123"}',
            '{"password": " FILTERED_PASSWORD "} {"password": " FILTERED_PASSWORD "}',
        ),
    ],
)
def test_mock_password(input_text, expected_output, formatter):
    assert formatter.mock_password(input_text) == expected_output


@pytest.mark.parametrize(
    "input_text, expected_output",
    [
        ('{"FLAIR": "[python]"}', '{"FLAIR": "[ FILTERED_FLAIR ]"}'),
        ('{"FLAIR": "[question]"}', '{"FLAIR": "[ FILTERED_FLAIR ]"}'),
        ('{"FLAIR": "[bug]"}', '{"FLAIR": "[ FILTERED_FLAIR ]"}'),
        ('{"FLAIR": "[feature]"}', '{"FLAIR": "[ FILTERED_FLAIR ]"}'),
        ('{"FLAIR": "[announcement]"}', '{"FLAIR": "[ FILTERED_FLAIR ]"}'),
        ('{"FLAIR": "[FILTERED_FLAIR]"}', '{"FLAIR": "[ FILTERED_FLAIR ]"}'),
    ],
)
def test_mock_flair(input_text, expected_output, formatter):
    assert formatter.mock_flair(input_text) == expected_output


@pytest.mark.parametrize(
    "input_text, expected_output",
    [
        (
            "This is C:\\Users\\username\\file.txt",
            "This is C:/Users/username/file.txt",
        ),
        ("No home directory here!", "No home directory here!"),
        (
            f"This is {os.path.expanduser('~')}\\file.txt",
            "This is MOCKING_USER_PATH/file.txt",
        ),
        (
            f"Some path: {os.path.expanduser('~/subfolder')}",
            "Some path: MOCKING_USER_PATH/subfolder",
        ),
    ],
)
def test_mock_home_directory(input_text, expected_output, formatter):
    assert formatter.mock_home_directory(input_text) == expected_output


@pytest.mark.parametrize(
    "input_text, expected_output",
    [
        (
            "This is a string with a\nnewline",
            "This is a string with a MOCKING_BREAKLINE newline",
        ),
        ("'Traceback occurred", "Traceback occurred"),
        ("No newlines or 'Traceback'", "No newlines or Traceback'"),
        ("'Traceback in the\nmiddle'", "Traceback in the MOCKING_BREAKLINE middle'"),
        (
            "Multiple\n\nnewlines",
            "Multiple MOCKING_BREAKLINE  MOCKING_BREAKLINE newlines",
        ),
    ],
)
def test_filter_special_tags(input_text, expected_output, formatter):
    assert formatter.filter_special_tags(input_text) == expected_output


@pytest.mark.parametrize(
    "input_text, expected_output",
    [
        (
            f"This is {os.path.expanduser('~')}\\file.txt",
            "This is MOCKING_USER_PATH/file.txt",
        ),
        ('{"FLAIR": "[announcement]"}', '{"FLAIR": "[ FILTERED_FLAIR ]"}'),
        ("Another email: alice@example.co.uk", "Another email:  FILTERED_EMAIL "),
        ("Another IP: 172.16.32.1", "Another IP:  FILTERED_IP "),
        ('{"password": "secure_pass_123"}', '{"password": " FILTERED_PASSWORD "}'),
    ],
)
def test_filter_piis(input_text, expected_output, formatter):
    assert formatter.filter_piis(input_text) == expected_output


@pytest.mark.parametrize(
    "input_text, expected_output",
    [
        (
            f"This is {os.path.expanduser('~')}\\file.txt",
            "This is MOCKING_USER_PATH/file.txt",
        ),
        ('{"FLAIR": "[announcement]"}', '{"FLAIR": "[ FILTERED_FLAIR ]"}'),
        ("Another email: alice@example.co.uk", "Another email:  FILTERED_EMAIL "),
        ("Another IP: 172.16.32.1", "Another IP:  FILTERED_IP "),
        ('{"password": "secure_pass_123"}', '{"password": " FILTERED_PASSWORD "}'),
        ("'Traceback in the\nmiddle'", "Traceback in the MOCKING_BREAKLINE middle'"),
    ],
)
def test_filter_log_line(input_text, expected_output, formatter):
    assert formatter.filter_log_line(input_text) == expected_output


def test_formatException_invalid():
    with pytest.raises(Exception):
        formatter.formatException(Exception("Big bad error"))


def test_format(formatter):
    # Prepare the log record
    log_record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="/path/to/module.py",
        lineno=42,
        msg="This is a test log message with | symbol",
        args=(),
        exc_info=None,
    )

    # Set up the mock objects
    formatter.calculate_level_name = Mock(return_value="INFO")
    formatter.filter_log_line = Mock(return_value="Filtered log message")

    # Call the format method
    formatted_log = formatter.format(log_record)

    # Assertions
    expected_log = "INFO|test_app_name|unknown-commit|test_app_id|test_session_id|test_user_id|Filtered log message"

    assert formatted_log == expected_log

    # Check if the mock methods were called
    formatter.calculate_level_name.assert_called_once()
    formatter.filter_log_line.assert_called_once()
