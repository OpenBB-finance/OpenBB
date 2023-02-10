import multiprocessing
import sys

from openbb_terminal.core.config.paths import load_dotenv_with_priority
from openbb_terminal.core.integration_tests import integration_controller
from openbb_terminal.session import session_controller
from openbb_terminal.terminal_helper import is_installer, is_auth_enabled

if __name__ == "__main__":
    multiprocessing.freeze_support()
    sent_args = sys.argv[1:]

    # When authentication is fully implemented
    # Remove the line below and references to is_auth_enabled
    load_dotenv_with_priority()

    if "-t" in sent_args or "--test" in sent_args:
        integration_controller.main()
    if is_auth_enabled():
        if is_installer() or "--login" in sent_args:
            session_controller.main()
        else:
            session_controller.launch_terminal()
    else:
        session_controller.launch_terminal()
