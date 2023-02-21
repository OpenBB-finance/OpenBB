import os
from openbb_terminal.base_helpers import load_env_vars

PLOT_DPI = load_env_vars("OPENBB_PLOT_DPI", int, 100, "settings")

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
PLOT_HEIGHT = load_env_vars("OPENBB_PLOT_HEIGHT", int, 500, "settings")
PLOT_WIDTH = load_env_vars("OPENBB_PLOT_WIDTH", int, 800, "settings")

# Used when USE_PLOT_AUTOSCALING is set to True
PLOT_HEIGHT_PERCENTAGE = load_env_vars(
    "OPENBB_PLOT_HEIGHT_PERCENTAGE", float, 50.0, "settings"
)
PLOT_WIDTH_PERCENTAGE = load_env_vars(
    "OPENBB_PLOT_WIDTH_PERCENTAGE", float, 70.0, "settings"
)

# When autoscaling is True, choose which monitor to scale to
# Primary monitor = 0, secondary monitor use 1
MONITOR = load_env_vars("OPENBB_MONITOR", int, 0, "settings")

# Color for `view` command data.  All pyplot colors listed at:
# https://matplotlib.org/stable/gallery/color/named_colors.html
VIEW_COLOR = "tab:green"
