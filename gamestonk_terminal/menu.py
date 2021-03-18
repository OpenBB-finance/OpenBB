import os

from matplotlib import pyplot

from prompt_toolkit import PromptSession
from prompt_toolkit.eventloop.inputhook import set_eventloop_with_inputhook
from prompt_toolkit.history import FileHistory


def inputhook(inputhook_context):
    while not inputhook_context.input_is_ready():
        pyplot.pause(0.1)
    return False


history_file = os.path.join(os.path.expanduser("~"), ".gamestonk_terminal.his")

try:
    session = PromptSession(history=FileHistory(history_file))
    set_eventloop_with_inputhook(inputhook)
except Exception as e:  # noqa: F841
    print("WARNING: Prompt toolkit is turned on but did not initialize succesfully. Falling back to input()...")
    session = None
