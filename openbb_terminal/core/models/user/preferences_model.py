from pydantic.dataclasses import dataclass


@dataclass(config=dict(validate_assignment=True))
class PreferencesModel:
    """Data model for preferences."""

    SYNC_ENABLED: bool = True
    TOOLBAR_TWEET_NEWS: bool = False


    # PLOT_BACKEND
    # Examples:
    # "tkAgg" - This uses the tkinter library.  If unsure, set to this
    # "module://backend_interagg" - This is what pycharm defaults to in Scientific Mode
    # "MacOSX" - Mac default.  Does not work with backtesting
    # "Qt5Agg" - This requires the PyQt5 package is installed
    # See more: https://matplotlib.org/stable/tutorials/introductory/usage.html#the-builtin-backends
    PLOT_BACKEND: str = None
