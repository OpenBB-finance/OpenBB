import logging
import sys
from typing import Optional

from matplotlib import pyplot
from prompt_toolkit import PromptSession
from prompt_toolkit.eventloop.inputhook import set_eventloop_with_inputhook
from prompt_toolkit.history import FileHistory

from openbb_terminal.core.config.paths import HIST_FILE_PATH
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


# pylint: disable=W0104
def is_jupyter() -> bool:
    try:
        __IPYTHON__  # type: ignore
        return True
    except NameError:
        return False


def is_papermill() -> bool:
    """Check if session is being launched with args '-m ipykernel_launcher',
    thus coming from papermill Popen. See 'ipykernel_launcher' in reports_model
    for more detail.
    """

    return all(
        i in sys.argv
        for i in [
            "-m",
            "ipykernel_launcher",
            "-f",
            "--HistoryManager.hist_file=:memory:",
        ]
    )


def inputhook(inputhook_context):
    while not inputhook_context.input_is_ready():
        try:
            pyplot.pause(0.1)
        except Exception as exp:
            logger.exception("%s", type(exp).__name__)
            continue
    return False


try:
    if sys.stdin.isatty():
        session: Optional[PromptSession] = PromptSession(
            history=FileHistory(str(HIST_FILE_PATH))
        )
        set_eventloop_with_inputhook(inputhook)
    else:
        session = None
# pylint: disable=unused-variable
except Exception as e:  # noqa: F841
    logger.exception("%s", type(e).__name__)
    console.print(
        "WARNING: Prompt toolkit is turned on but did not initialize successfully."
        " Falling back to input()..."
    )
    session = None  # type: ignore
