import os

import dotenv

from openbb_terminal.core.config.paths import USER_ENV_FILE, REPOSITORY_ENV_FILE
from openbb_terminal.rich_config import console

dotenv.load_dotenv(USER_ENV_FILE)
dotenv.load_dotenv(REPOSITORY_ENV_FILE, override=True)

try:
    PLOT_DPI = int(os.getenv("OPENBB_PLOT_DPI", "100"))
except ValueError:
    PLOT_DPI = 100
    console.print(
        f"[red]OPENBB_PLOT_DPI is not an integer, using default value of {PLOT_DPI}[/red]"
    )

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
try:
    PLOT_HEIGHT = int(os.getenv("OPENBB_PLOT_HEIGHT", "500"))
except ValueError:
    PLOT_HEIGHT = 500
    console.print(
        "[red] Invalid value for OPENBB_PLOT_HEIGHT. Please use a number.[/red]\n"
    )
try:
    PLOT_WIDTH = int(os.getenv("OPENBB_PLOT_WIDTH", "800"))
except ValueError:
    PLOT_WIDTH = 800
    console.print(
        "[red] Invalid value for OPENBB_PLOT_WIDTH. Please use a number.[/red]\n"
    )

# Used when USE_PLOT_AUTOSCALING is set to True
try:
    PLOT_HEIGHT_PERCENTAGE = float(os.getenv("OPENBB_PLOT_HEIGHT_PERCENTAGE", "50.00"))
except ValueError:
    PLOT_HEIGHT_PERCENTAGE = 50.00
    console.print(
        "[red] Invalid value for OPENBB_PLOT_HEIGHT_PERCENTAGE. Please use a number.[/red]\n"
    )
try:
    PLOT_WIDTH_PERCENTAGE = float(os.getenv("OPENBB_PLOT_WIDTH_PERCENTAGE", "70.00"))
except ValueError:
    PLOT_WIDTH_PERCENTAGE = 70.00
    console.print(
        "[red] Invalid value for OPENBB_PLOT_WIDTH_PERCENTAGE. Please use a number.[/red]\n"
    )

# When autoscaling is True, choose which monitor to scale to
# Primary monitor = 0, secondary monitor use 1
MONITOR = int(os.getenv("OPENBB_MONITOR", "0"))

# Color for `view` command data.  All pyplot colors listed at:
# https://matplotlib.org/stable/gallery/color/named_colors.html
VIEW_COLOR = "tab:green"
