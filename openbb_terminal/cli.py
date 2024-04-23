import sys

import openbb_terminal.core.config.config_terminal as cfg
from openbb_terminal.core.session import session_controller


def main():
    cfg.setup_config_terminal()

    dev = "--dev" in sys.argv[1:]
    debug = "--debug" in sys.argv[1:]

    session_controller.launch_terminal(dev=dev, debug=debug)


if __name__ == "__main__":
    main()
