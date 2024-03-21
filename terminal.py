import sys

# pylint:disable=wrong-import-position

import openbb_terminal.config_terminal as cfg  # noqa: E402

# pylint:disable=unused-import,import-outside-toplevel
import openbb_terminal.core.session.current_system as syst  # noqa: F401,E402


def main():
    sent_args = sys.argv[1:]
    cfg.setup_config_terminal()

    if "-t" in sent_args or "--test" in sent_args:
        from openbb_terminal.core.integration_tests import integration_controller

        integration_controller.main()
    else:
        from openbb_terminal.core.session import session_controller

        dev = "--dev" in sys.argv[1:]
        debug = "--debug" in sys.argv[1:]

        session_controller.launch_terminal(dev=dev, debug=debug)


if __name__ == "__main__":
    main()
