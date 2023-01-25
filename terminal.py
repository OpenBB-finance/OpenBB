import multiprocessing
import sys

if __name__ == "__main__":
    multiprocessing.freeze_support()
    sent_args = sys.argv[1:]
    if "-t" in sent_args or "--test" in sent_args:
        from openbb_terminal.core.integration_tests import integration_controller

        integration_controller.main()
    else:
        from openbb_terminal.session import session_controller
        from openbb_terminal.terminal_helper import is_packaged_application

        session_controller.main(guest_allowed=not is_packaged_application())
