import os

import dotenv

from openbb_terminal.core.config.paths import USER_ENV_FILE, REPOSITORY_ENV_FILE
from openbb_terminal import base_helpers

dotenv.load_dotenv(USER_ENV_FILE)
dotenv.load_dotenv(REPOSITORY_ENV_FILE, override=True)

PLOT_DPI = base_helpers.load_env_vars("OPENBB_PLOT_DPI", int, 100)

# Backend to use for plotting
BACKEND = os.getenv("OPENBB_BACKEND", "None")
if BACKEND == "None":
    BACKEND = None  # type: ignore
# Examples:
# "tkAgg" - This uses the tkinter library.  If unsure, set to this
# "module://backend_interagg" - This is what pycharm defaults to in Scientific Mode
# "MacOSX" - Mac default.  Does not work with backtesting
# "Qt5Agg" - This requires the PyQt5 package is installed
# See more: https://matplotlib.org/stable/tutorials/introductory/usage.html#the-builtin-backends

# Used when USE_PLOT_AUTOSCALING is set to False
PLOT_HEIGHT = base_helpers.load_env_vars("OPENBB_PLOT_HEIGHT", int, 500)
PLOT_WIDTH = base_helpers.load_env_vars("OPENBB_PLOT_WIDTH", int, 800)

# Used when USE_PLOT_AUTOSCALING is set to True
PLOT_HEIGHT_PERCENTAGE = base_helpers.load_env_vars(
    "OPENBB_PLOT_HEIGHT_PERCENTAGE", float, 50.0
)
PLOT_WIDTH_PERCENTAGE = base_helpers.load_env_vars(
    "OPENBB_PLOT_WIDTH_PERCENTAGE", float, 70.0
)

# When autoscaling is True, choose which monitor to scale to
# Primary monitor = 0, secondary monitor use 1
MONITOR = base_helpers.load_env_vars("OPENBB_MONITOR", int, 0)

# Color for `view` command data.  All pyplot colors listed at:
# https://matplotlib.org/stable/gallery/color/named_colors.html
VIEW_COLOR = "tab:green"
