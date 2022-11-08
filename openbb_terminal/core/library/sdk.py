from openbb_terminal.core.library.breadcrumb import Breadcrumb
from openbb_terminal.core.library.trail_map import TrailMap
from openbb_terminal.core.library.breadcrumb import MetadataBuilder
from openbb_terminal.reports.reports_controller import ReportController
from openbb_terminal.dashboards.dashboards_controller import DashboardsController

from traceback import format_stack


trail = ""
trail_map = TrailMap()
metadata = MetadataBuilder.build(trail=trail, trail_map=trail_map)


SUPPRESS_LOGGING_CLASSES = {
    ReportController: "ReportController",
    DashboardsController: "DashboardsController",
}


def check_suppress_logging(suppress_dict: dict) -> bool:
    """
    Check if logging should be suppressed.
    If the dict contains a value that is found in the stack trace,
     the logging should be suppressed.

    Parameters
    ----------
    supress_dict: dict
        Dictionary with values that trigger log suppression

    Returns
    -------
    bool
        True if logging shall be suppressed, False otherwise
    """
    for ele in format_stack():
        for _, value in suppress_dict.items():
            if value in ele:
                return True

    return False


openbb = Breadcrumb(
    metadata=metadata,
    trail=trail,
    trail_map=trail_map,
    suppress_logging=check_suppress_logging(suppress_dict=SUPPRESS_LOGGING_CLASSES),
)
