import multiprocessing
import sys

from openbb_terminal.core.integration_tests import integration_controller
from openbb_terminal.session import session_controller
from openbb_terminal.terminal_helper import is_installer

if __name__ == "__main__":
    multiprocessing.freeze_support()
    sent_args = sys.argv[1:]
    if "-t" in sent_args or "--test" in sent_args:
        integration_controller.main()
    else:
        session_controller.main(guest_allowed=not is_installer())
