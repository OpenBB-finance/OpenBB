import multiprocessing
import os
import sys
from openbb_terminal.core.config.paths import load_dotenv_with_priority

from openbb_terminal.core.integration_tests import integration_controller
from openbb_terminal.session import session_controller
from openbb_terminal.terminal_helper import is_installer
from openbb_terminal.base_helpers import strtobool

if __name__ == "__main__":
    multiprocessing.freeze_support()
    sent_args = sys.argv[1:]

    # Remove these 2 lines when authentication is fully implemented
    load_dotenv_with_priority()
    auth_enabled = strtobool(os.getenv("OPENBB_ENABLE_AUTHENTICATION"))

    if "-t" in sent_args or "--test" in sent_args:
        integration_controller.main()
    elif auth_enabled:
        if is_installer():
            session_controller.main(guest_allowed=False)
        elif "-u" in sent_args or "--user-auth" in sent_args:
            if "-u" in sys.argv:
                sys.argv.remove("-u")
            if "--user-auth" in sys.argv:
                sys.argv.remove("--user-auth")
            session_controller.main(guest_allowed=True)
    else:
        session_controller.launch_terminal()
