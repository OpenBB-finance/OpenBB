"""OpenBB Platform CLI entry point."""

import sys

from src.config.setup import setup_config_terminal
from src.session import launch_terminal


def main():
    """Use the main entry point for the OpenBB Terminal CLI."""
    setup_config_terminal()

    dev = "--dev" in sys.argv[1:]
    debug = "--debug" in sys.argv[1:]

    launch_terminal(dev=dev, debug=debug)


if __name__ == "__main__":
    main()
