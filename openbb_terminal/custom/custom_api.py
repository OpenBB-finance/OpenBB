"""Custom context API."""
# flake8: noqa
# pylint: disable=unused-import

# Context menus
from .custom_view import custom_plot as plot
from .quantitative_analysis import qa_api as qa

try:
    from .prediction_techniques import pred_api as pred
except Exception:
    # print("Prediction API is not available.")
    pass
