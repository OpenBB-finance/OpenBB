import sys
from multiprocessing import freeze_support

import openbb_terminal.config_terminal as cfg

# pylint:disable=unused-import,import-outside-toplevel
import openbb_terminal.core.session.current_system as syst  # noqa: F401
import openbb_terminal.core.session.current_user as user  # noqa: F401
from openbb_terminal.terminal_helper import is_auth_enabled, is_installer


def main():
    sent_args = sys.argv[1:]

    cfg.setup_config_terminal()

    if "-t" in sent_args or "--test" in sent_args:
        from openbb_terminal.core.integration_tests import integration_controller

        integration_controller.main()
    else:
        from openbb_terminal.core.session import session_controller

        if is_auth_enabled() and ("--login" in sys.argv[1:] or is_installer()):
            session_controller.main()
        else:
            session_controller.launch_terminal()


if __name__ == "__main__":
    freeze_support()
    main()
