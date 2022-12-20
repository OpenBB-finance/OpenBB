import sys

from openbb_terminal import integration_testing, terminal_controller
from openbb_terminal.qt_app.plotly_helper import BACKEND

if __name__ == "__main__":
    BACKEND.start()

    sent_args = sys.argv[1:]
    if "-t" in sent_args or "--test" in sent_args:
        integration_testing.parse_args_and_run()
    else:
        terminal_controller.parse_args_and_run()
