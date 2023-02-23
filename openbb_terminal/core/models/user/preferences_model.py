from pydantic.dataclasses import dataclass
from pydantic import PositiveInt, PositiveFloat, NonNegativeInt


@dataclass(config=dict(validate_assignment=True))
class PreferencesModel:
    """Data model for preferences."""

    SYNC_ENABLED: bool = True
    TOOLBAR_TWEET_NEWS: bool = False


    # BACKEND
    # Examples:
    # "tkAgg" - This uses the tkinter library.  If unsure, set to this
    # "module://backend_interagg" - This is what pycharm defaults to in Scientific Mode
    # "MacOSX" - Mac default.  Does not work with backtesting
    # "Qt5Agg" - This requires the PyQt5 package is installed
    # See more: https://matplotlib.org/stable/tutorials/introductory/usage.html#the-builtin-backends
    BACKEND: str = None
    PLOT_DPI: int = PositiveInt
