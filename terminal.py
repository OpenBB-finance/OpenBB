import os
from openbb_terminal.terminal_controller import parse_args_and_run

# Supress this warning:
# 0.00s - Debugger warning: The os.path.realpath.__code__.co_filename (posixpath.py)
# 0.00s - is not absolute, which may make the debugger miss breakpoints.
# 0.00s - Note: Debugging will proceed. Set PYDEVD_DISABLE_FILE_VALIDATION=1 to disable this validation.
os.environ["PYDEVD_DISABLE_FILE_VALIDATION"] = "1"

if __name__ == "__main__":
    parse_args_and_run()
