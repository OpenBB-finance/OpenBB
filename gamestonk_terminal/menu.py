import os

from matplotlib import pyplot

from prompt_toolkit import PromptSession
from prompt_toolkit.eventloop.inputhook import set_eventloop_with_inputhook
from prompt_toolkit.history import FileHistory


def inputhook(inputhook_context):
    while not inputhook_context.input_is_ready():
        try:
            pyplot.pause(0.1)
        # pylint: disable=unused-variable
        except Exception:  # noqa: F841
            continue
    return False


history_file = os.path.join(os.path.expanduser("~"), ".gamestonk_terminal.his")

try:
    session = PromptSession(history=FileHistory(history_file))
    set_eventloop_with_inputhook(inputhook)
# pylint: disable=unused-variable
except Exception as e:  # noqa: F841
    print(
        "WARNING: Prompt toolkit is turned on but did not initialize successfully. Falling back to input()..."
    )
    session = None
