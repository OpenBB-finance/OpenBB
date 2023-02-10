import multiprocessing
import os
import sys
from openbb_terminal.core.config.paths import load_dotenv_with_priority

from openbb_terminal.core.integration_tests import integration_controller
from openbb_terminal.session import session_controller
from openbb_terminal.terminal_helper import is_installer

if __name__ == "__main__":
    multiprocessing.freeze_support()
    sent_args = sys.argv[1:]

    # Remove this line when authentication is fully implemented
    # and remove the OPENBB_ENABLE_AUTHENTICATION variable
    load_dotenv_with_priority()

    if "-t" in sent_args or "--test" in sent_args:
        integration_controller.main()
    if str(os.getenv("OPENBB_ENABLE_AUTHENTICATION")).lower() == "true":
        if is_installer():
            session_controller.main(guest_allowed=False)
        elif "-u" in sent_args or "--user-auth" in sent_args:
            session_controller.main(guest_allowed=True)
        else:
            session_controller.launch_terminal()
    else:
        session_controller.launch_terminal()
