import multiprocessing
import sys
from openbb_terminal import terminal_controller
from openbb_terminal.integration_tests import integration_controller

if __name__ == "__main__":
    sent_args = sys.argv[1:]
    if "-t" in sent_args or "--test" in sent_args:
        multiprocessing.freeze_support()
        integration_controller.main()
    else:
        terminal_controller.parse_args_and_run()
