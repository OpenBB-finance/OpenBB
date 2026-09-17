"""Backwards-compatibility shim coverage.

The V5 reorganization moved code into ``models/`` / ``app/`` /
``service/`` subpackages. The legacy import paths are preserved as
shim modules; these tests assert each one re-exports the public
surface so external callers keep working without code changes.
"""


def test_query_models_shim_re_exports_omni_widget_input():
    """``openbb_platform_api.query_models.OmniWidgetInput`` is the
    same class as ``openbb_platform_api.models.query.OmniWidgetInput``.
    """
    from openbb_platform_api import query_models
    from openbb_platform_api.models.query import OmniWidgetInput

    assert query_models.OmniWidgetInput is OmniWidgetInput
    assert "OmniWidgetInput" in query_models.__all__


def test_response_models_shim_re_exports_response_classes():
    """``openbb_platform_api.response_models`` exposes the V5
    response-model classes verbatim.
    """
    from openbb_platform_api import response_models
    from openbb_platform_api.models.response import (
        MetricResponseModel,
        OmniWidgetResponseModel,
        PdfResponseModel,
    )

    assert response_models.MetricResponseModel is MetricResponseModel
    assert response_models.OmniWidgetResponseModel is OmniWidgetResponseModel
    assert response_models.PdfResponseModel is PdfResponseModel


def test_utils_merge_apps_shim_re_exports_apps_service():
    """``utils.merge_apps`` shim points at the V5 service module."""
    from openbb_platform_api.service.apps_service import (
        get_additional_apps,
        has_additional_apps,
    )
    from openbb_platform_api.utils import merge_apps

    assert merge_apps.has_additional_apps is has_additional_apps
    assert merge_apps.get_additional_apps is get_additional_apps


def test_utils_merge_agents_shim_re_exports_agents_service():
    """``utils.merge_agents`` shim points at the V5 service module."""
    from openbb_platform_api.service.agents_service import (
        get_additional_agents,
        has_additional_agents,
    )
    from openbb_platform_api.utils import merge_agents

    assert merge_agents.has_additional_agents is has_additional_agents
    assert merge_agents.get_additional_agents is get_additional_agents


def test_utils_api_shim_re_exports_split_helpers():
    """``utils.api`` shim covers all the split-out helpers — args,
    bootstrap, network, widgets_service — under the legacy name.
    """
    from openbb_platform_api.app.args import (
        LAUNCH_SCRIPT_DESCRIPTION,
        parse_args,
    )
    from openbb_platform_api.app.bootstrap import import_app
    from openbb_platform_api.service.widgets_service import get_widgets_json
    from openbb_platform_api.utils import api as api_shim
    from openbb_platform_api.utils.network import check_port, get_user_settings

    assert api_shim.parse_args is parse_args
    assert api_shim.LAUNCH_SCRIPT_DESCRIPTION is LAUNCH_SCRIPT_DESCRIPTION
    assert api_shim.import_app is import_app
    assert api_shim.check_port is check_port
    assert api_shim.get_user_settings is get_user_settings
    assert api_shim.get_widgets_json is get_widgets_json


def test_utils_api_shim_first_run_and_path_widgets_proxy_to_service():
    """``FIRST_RUN`` and ``PATH_WIDGETS`` go through ``__getattr__`` so
    reads always reflect the live service state — not a stale snapshot.
    """
    from openbb_platform_api.service import widgets_service
    from openbb_platform_api.utils import api as api_shim

    # Mutate the canonical state and confirm the shim reflects it.
    original_first_run = widgets_service.FIRST_RUN
    original_path_widgets = widgets_service.PATH_WIDGETS
    try:
        widgets_service.FIRST_RUN = False
        widgets_service.PATH_WIDGETS = {"x": {"some": "widget"}}
        assert api_shim.FIRST_RUN is False
        assert api_shim.PATH_WIDGETS == {"x": {"some": "widget"}}
    finally:
        widgets_service.FIRST_RUN = original_first_run
        widgets_service.PATH_WIDGETS = original_path_widgets


def test_main_module_re_exports_app_app_namespace():
    """``openbb_platform_api.main`` is the canonical entry point uvicorn
    consumes via ``main:app``. The shim must surface ``app``,
    ``main``, ``launch_api``, and the route handlers from the V5
    ``app.app`` module.
    """
    from openbb_platform_api import main as main_shim
    from openbb_platform_api.app import app as v5_app_module

    for name in ("app", "main", "launch_api", "logger", "openapi"):
        assert getattr(main_shim, name) is getattr(v5_app_module, name)


def test_utils_api_shim_unknown_attr_raises():
    """Unknown attribute access on the shim raises a clean ``AttributeError``
    (not the catch-all module-not-found ``__getattr__`` returns ``None`` of
    a sloppy implementation).
    """
    import pytest

    from openbb_platform_api.utils import api as api_shim

    with pytest.raises(AttributeError):
        _ = api_shim.no_such_attribute


def test_utils_api_shim_dir_lists_lazy_targets():
    """``dir(api_shim)`` surfaces the lazy re-exported names so IDE
    autocomplete / ``inspect.getmembers`` users see the same surface
    they'd get from a non-shim module. The set must include each
    legacy name we're proxying.
    """
    from openbb_platform_api.utils import api as api_shim

    listed = dir(api_shim)
    # Spot-check the whole legacy surface — if any of these names
    # disappears the shim has silently regressed.
    for name in (
        "LAUNCH_SCRIPT_DESCRIPTION",
        "parse_args",
        "import_app",
        "get_widgets_json",
        "logger",
        "FIRST_RUN",
        "PATH_WIDGETS",
        "check_port",
        "get_user_settings",
    ):
        assert name in listed
    # Output is stable / sorted so callers can rely on ordering.
    assert listed == sorted(listed)
