"""OpenBB Platform CLI entry point."""

import sys

from openbb_cli.config.setup import bootstrap
from openbb_cli.controllers.cli_controller import launch


def main():
    """Use the main entry point for the OpenBB CLI."""
    bootstrap()

    dev = "--dev" in sys.argv[1:]
    debug = "--debug" in sys.argv[1:]

    launch(dev, debug)


if __name__ == "__main__":
    main()
