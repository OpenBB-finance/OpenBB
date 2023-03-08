import sys
from multiprocessing import freeze_support

import openbb_terminal.config_terminal as cfg # noqa: F401
import openbb_terminal.core.session.current_user as _  # noqa: F401
from openbb_terminal.terminal_helper import is_auth_enabled

# pylint: disable=import-outside-toplevel


def main():
    sent_args = sys.argv[1:]

    if "-t" in sent_args or "--test" in sent_args:
        from openbb_terminal.core.integration_tests import integration_controller

        integration_controller.main()
    else:
        from openbb_terminal.core.session import session_controller

        if is_auth_enabled():
            session_controller.main()
        else:
            session_controller.launch_terminal()


if __name__ == "__main__":
    freeze_support()
    main()
