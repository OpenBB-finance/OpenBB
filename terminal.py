import multiprocessing
import sys

from openbb_terminal.base_helpers import load_dotenv_and_reload_configs
from openbb_terminal.core.integration_tests import integration_controller
from openbb_terminal.session import session_controller
from openbb_terminal.terminal_helper import is_auth_enabled, is_installer

if __name__ == "__main__":
    multiprocessing.freeze_support()
    sent_args = sys.argv[1:]

    load_dotenv_and_reload_configs()

    if "-t" in sent_args or "--test" in sent_args:
        integration_controller.main()
    if is_auth_enabled():
        if is_installer() or "--login" in sent_args:
            session_controller.main()
        else:
            session_controller.launch_terminal()
    else:
        session_controller.launch_terminal()
