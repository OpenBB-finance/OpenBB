"""OpenBB Platform CLI entry point."""

import sys

from openbb_cli.utils.utils import change_logging_sub_app, reset_logging_sub_app


def main():
    """Use the main entry point for the OpenBB Platform CLI."""
    print("Loading...\n")  # noqa: T201

    # pylint: disable=import-outside-toplevel
    from openbb_cli.config.setup import bootstrap
    from openbb_cli.controllers.cli_controller import launch

    bootstrap()

    dev = "--dev" in sys.argv[1:]
    debug = "--debug" in sys.argv[1:]

    launch(dev, debug)


if __name__ == "__main__":
    initial_logging_sub_app = change_logging_sub_app()
    try:
        main()
    except Exception:
        pass
    finally:
        reset_logging_sub_app(initial_logging_sub_app)
