import multiprocessing
import sys

from openbb_terminal.base_helpers import load_dotenv_and_reload_configs
import openbb_terminal.config_terminal as cfg
from openbb_terminal.terminal_helper import is_auth_enabled

# pylint: disable=import-outside-toplevel


def main():
    multiprocessing.freeze_support()
    sent_args = sys.argv[1:]

    load_dotenv_and_reload_configs()

    if "-t" in sent_args or "--test" in sent_args:
        from openbb_terminal.core.integration_tests import integration_controller

        integration_controller.main()
    else:
        from openbb_terminal.session import session_controller

        if is_auth_enabled():
            session_controller.main()
        else:
            cfg.Credentials.load_from_dotenv()
            session_controller.launch_terminal()


if __name__ == "__main__":
    main()
