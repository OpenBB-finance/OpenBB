import pytest

from openbb_terminal.session import session_controller


@pytest.mark.record_stdout
def test_display_welcome_message():
    session_controller.display_welcome_message()
