"""Service-layer modules for the OpenBB Platform API extension.

Each service owns one of the launcher's data-orchestration flows
(widgets / apps / agents). The FastAPI route handlers in
``app/app.py`` thin-wrap these services so the request shape and the
catalogue-building logic stay separable.
"""

from openbb_platform_api.service.agents_service import (
    get_additional_agents,
    has_additional_agents,
)
from openbb_platform_api.service.apps_service import (
    get_additional_apps,
    has_additional_apps,
)
from openbb_platform_api.service.widgets_service import (
    FIRST_RUN,
    PATH_WIDGETS,
    get_widgets_json,
)

__all__ = [
    "FIRST_RUN",
    "PATH_WIDGETS",
    "get_additional_agents",
    "get_additional_apps",
    "get_widgets_json",
    "has_additional_agents",
    "has_additional_apps",
]
