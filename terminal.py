import multiprocessing
import os
import sys
from openbb_terminal.core.config.paths import load_dotenv_with_priority

from openbb_terminal.core.integration_tests import integration_controller
from openbb_terminal.session import session_controller
from openbb_terminal.session.session_model import clear_openbb_env_vars
from openbb_terminal.terminal_helper import is_installer

if __name__ == "__main__":
    multiprocessing.freeze_support()
    sent_args = sys.argv[1:]
    load_dotenv_with_priority()
    auth = str(os.getenv("OPENBB_ENABLE_AUTHENTICATION")).lower()
    clear_openbb_env_vars()

    if "-t" in sent_args or "--test" in sent_args:
        integration_controller.main()
    elif auth == "true":
        session_controller.main(guest_allowed=not is_installer())
    else:
        session_controller.launch_terminal()
