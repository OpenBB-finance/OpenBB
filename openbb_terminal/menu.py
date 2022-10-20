from typing import Optional
import logging
import os

from matplotlib import pyplot
from prompt_toolkit import PromptSession
from prompt_toolkit.eventloop.inputhook import set_eventloop_with_inputhook
from prompt_toolkit.history import FileHistory

logger = logging.getLogger(__name__)


# pylint: disable=W0104
def is_jupyter() -> bool:
    try:
        __IPYTHON__  # type: ignore
        return True
    except NameError:
        return False


def inputhook(inputhook_context):
    while not inputhook_context.input_is_ready():
        try:
            pyplot.pause(0.1)
        except Exception as exp:
            logger.exception("%s", type(exp).__name__)
            continue
    return False


history_file = os.path.join(os.path.expanduser("~"), ".openbb_terminal.his")

try:
    if not is_jupyter():
        session: Optional[PromptSession] = PromptSession(
            history=FileHistory(history_file)
        )
        set_eventloop_with_inputhook(inputhook)
    else:
        session = None
# pylint: disable=unused-variable
except Exception as e:  # noqa: F841
    logger.exception("%s", type(e).__name__)
    print(
        "WARNING: Prompt toolkit is turned on but did not initialize successfully."
        " Falling back to input()..."
    )
    session = None  # type: ignore
