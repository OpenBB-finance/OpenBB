import multiprocessing
import sys
from openbb_terminal import terminal_controller
from openbb_terminal.core.integration_tests import integration_controller
from openbb_terminal.account import login_wizard
from openbb_terminal.terminal_helper import is_packaged_application


if __name__ == "__main__":
    multiprocessing.freeze_support()
    sent_args = sys.argv[1:]
    if "-t" in sent_args or "--test" in sent_args:
        integration_controller.main()
    elif (
        is_packaged_application() or True
    ):  # remove True to force login just on installer
        login_wizard.main()
    else:
        terminal_controller.parse_args_and_run()
