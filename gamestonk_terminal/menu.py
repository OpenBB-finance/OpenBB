import os

from matplotlib import pyplot

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory

history_file = os.path.join(os.path.expanduser("~"), ".gamestonk_terminal.his")

try:
    session = PromptSession(history=FileHistory(history_file), inputhook=pyplot.draw)
except Exception as e:  # noqa: F841
    session = None
