"""OpenBB Platform CLI entry point."""

import sys

from openbb_terminal.config.setup import setup_config_terminal
from openbb_terminal.controllers.terminal_controller import launch


def main():
    """Use the main entry point for the OpenBB Terminal CLI."""
    setup_config_terminal()

    dev = "--dev" in sys.argv[1:]
    debug = "--debug" in sys.argv[1:]

    launch(dev, debug)


if __name__ == "__main__":
    main()
