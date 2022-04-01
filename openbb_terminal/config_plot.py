import os

PLOT_DPI = int(os.getenv("OBBFF_PLOT_DPI", "100"))

# Backend to use for plotting
BACKEND = os.getenv("OBBFF_BACKEND", "None")
if BACKEND == "None":
    BACKEND = None  # type: ignore
# Examples:
# "tkAgg" - This uses the tkinter library.  If unsure, set to this
# "module://backend_interagg" - This is what pycharm defaults to in Scientific Mode
# "MacOSX" - Mac default.  Does not work with backtesting
# "Qt5Agg" - This requires the PyQt5 package is installed
# See more: https://matplotlib.org/stable/tutorials/introductory/usage.html#the-builtin-backends

# Used when USE_PLOT_AUTOSCALING is set to False
PLOT_HEIGHT = int(os.getenv("OBBFF_PLOT_HEIGHT", "500"))
PLOT_WIDTH = int(os.getenv("OBBFF_PLOT_WIDTH", "800"))

# Used when USE_PLOT_AUTOSCALING is set to True
PLOT_HEIGHT_PERCENTAGE = float(os.getenv("OBBFF_PLOT_HEIGHT_PERCENTAGE", "50.00"))
PLOT_WIDTH_PERCENTAGE = float(os.getenv("OBBFF_PLOT_WIDTH_PERCENTAGE", "70.00"))

# When autoscaling is True, choose which monitor to scale to
# Primary monitor = 0, secondary monitor use 1
MONITOR = int(os.getenv("OBBFF_MONITOR", "0"))

# Color for `view` command data.  All pyplot colors listed at:
# https://matplotlib.org/stable/gallery/color/named_colors.html
VIEW_COLOR = "tab:green"
