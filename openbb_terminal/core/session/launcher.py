"""Launcher for terminal."""

from typing import List, Optional


# pylint: disable=inconsistent-return-statements
def launch_terminal(
    debug: bool = False, dev: bool = False, queue: Optional[List[str]] = None
):
    """Launch terminal."""
    # pylint: disable=import-outside-toplevel
    from openbb_terminal.core.controllers import terminal_controller

    if queue:
        return terminal_controller.main(debug, dev, queue, module="")

    terminal_controller.parse_args_and_run()
