import os

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory

history_file = os.path.join(os.path.expanduser("~"), ".gamestonk_terminal.his")

try:
    session = PromptSession(history=FileHistory(history_file))
except Exception as e:
    session = None
