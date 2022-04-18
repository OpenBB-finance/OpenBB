from pathlib import Path
from openbb_terminal.core.log.generation import settings


log = settings.LogSettings(Path("."), "H", "stdout,stderr,noop,file", True, 2)


def test_handler_list():
    value = log.handler_list
    assert value is not None


def test_verbosity():
    value = log.verbosity
    assert value is not None
