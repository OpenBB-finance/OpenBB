from unittest.mock import patch
import pytest

from openbb_terminal.session import session_controller


@pytest.mark.record_stdout
def test_display_welcome_message():
    session_controller.display_welcome_message()


@pytest.mark.record_stdout
@patch("openbb_terminal.session.session_controller.PromptSession")
def test_get_user_input(mock_prompt_session):
    # Arrange
    mock_prompt_session().prompt.side_effect = ["test@example.com", "password", "n"]

    # Act
    result = session_controller.get_user_input()

    # Assert
    assert result == ("test@example.com", "password", False)


@pytest.mark.record_stdout
@patch("openbb_terminal.session.session_controller.PromptSession")
def test_get_user_input_with_save(mock_prompt_session):
    # Arrange
    mock_prompt_session().prompt.side_effect = ["test@example.com", "password", "y"]

    # Act
    result = session_controller.get_user_input()

    # Assert
    assert result == ("test@example.com", "password", True)
