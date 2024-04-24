"""OpenBB Terminal CLI entry point."""

import sys

import openbb_terminal.core.config.config_terminal as cfg
from openbb_terminal.core.session import launcher


def main():
    """Use the main entry point for the OpenBB Terminal CLI."""
    cfg.setup_config_terminal()

    dev = "--dev" in sys.argv[1:]
    debug = "--debug" in sys.argv[1:]

    launcher.launch_terminal(dev=dev, debug=debug)


if __name__ == "__main__":
    main()
