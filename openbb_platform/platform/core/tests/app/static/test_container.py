"""Test the container.py file."""

from openbb_core.app.command_runner import CommandRunner
from openbb_core.app.static.container import Container


def test_container_init():
    """Test container init."""
    container = Container(CommandRunner())
    assert container
