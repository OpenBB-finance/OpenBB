"Test the Session class."

from unittest.mock import MagicMock, patch

import pytest
from openbb_cli.models.settings import Settings
from openbb_cli.session import Session, sys

# pylint: disable=redefined-outer-name, unused-argument, protected-access


def mock_isatty(return_value):
    """Mock the isatty method."""
    original_isatty = sys.stdin.isatty
    sys.stdin.isatty = MagicMock(return_value=return_value)  # type: ignore
    return original_isatty


@pytest.fixture
def session():
    """Session fixture."""
    return Session()


def test_session_initialization(session):
    """Test the initialization of the Session class."""
    assert session.settings is not None
    assert session.style is not None
    assert session.console is not None
    assert session.obbject_registry is not None
    assert isinstance(session.settings, Settings)


@patch("openbb_cli.session.PromptSession")
@patch("sys.stdin.isatty", return_value=True)
def test_get_prompt_session_true(mock_isatty, mock_prompt_session, session):
    "Test get_prompt_session method."
    prompt_session = session._get_prompt_session()
    assert prompt_session is not None


@patch("sys.stdin.isatty", return_value=False)
def test_get_prompt_session_false(mock_isatty, session):
    "Test get_prompt_session method."
    prompt_session = session._get_prompt_session()
    assert prompt_session is None
