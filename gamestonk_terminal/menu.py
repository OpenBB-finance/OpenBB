import logging
import os

from matplotlib import pyplot
from prompt_toolkit import PromptSession
from prompt_toolkit.eventloop.inputhook import set_eventloop_with_inputhook
from prompt_toolkit.history import FileHistory
from gamestonk_terminal.rich_config import console

logger = logging.getLogger(__name__)


def inputhook(inputhook_context):
    while not inputhook_context.input_is_ready():
        try:
            pyplot.pause(0.1)
        except Exception as exp:
            logger.exception("%s", type(exp).__name__)
            continue
    return False


history_file = os.path.join(os.path.expanduser("~"), ".gamestonk_terminal.his")

try:
    session = PromptSession(history=FileHistory(history_file))  # type: ignore
    set_eventloop_with_inputhook(inputhook)
# pylint: disable=unused-variable
except Exception as e:  # noqa: F841
    logger.exception("%s", type(e).__name__)
    console.print(
        "WARNING: Prompt toolkit is turned on but did not initialize successfully. Falling back to input()..."
    )
    session = None  # type: ignore
