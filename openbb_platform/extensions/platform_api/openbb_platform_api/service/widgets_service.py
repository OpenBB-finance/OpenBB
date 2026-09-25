"""Build / read / serve the Workspace ``widgets.json`` catalogue.

Higher-level orchestration around ``utils/widgets.build_json``: handles
the editable-on-disk flow (build → diff → prompt-to-merge → write) and
the ephemeral in-memory build path. Holds the launcher's mutable state
(``FIRST_RUN``, ``PATH_WIDGETS``) that the FastAPI route handlers in
``app/app.py`` consult.
"""

import json
import logging
import os
import sys
from pathlib import Path

from deepdiff import DeepDiff
from fastapi import FastAPI

logger = logging.getLogger("openbb_platform_api")

# Mutable launcher state. ``FIRST_RUN`` flips to ``False`` on the very
# first ``/widgets.json`` request so the cached build can be served
# verbatim instead of recomputed; ``PATH_WIDGETS`` accumulates router-
# defined widget definitions so they merge into the auto-generated set.
PATH_WIDGETS: dict = {}
FIRST_RUN: bool = True


def get_widgets_json(  # noqa: PLR0912
    _build: bool,
    _openapi: dict,
    widget_exclude_filter: list,
    editable: bool = False,
    widgets_path: str | None = None,
    app: FastAPI | None = None,
) -> dict:
    """Return the widgets.json contents the Workspace expects.

    Two modes:

    * **Editable** (``editable=True``): widgets.json lives on disk at
      ``widgets_path`` (or ``<env>/assets/widgets.json``). On
      ``_build=True`` the function rebuilds from the current openapi,
      diffs against the file, and (when there are changes) prompts the
      user interactively to overwrite / append-only / ignore. The
      chosen result is written back so subsequent loads are cheap.
    * **Ephemeral** (``editable=False``): rebuild every call from the
      live openapi; merge in any router-attached widgets that
      ``has_additional_widgets(app)`` discovered. Nothing touches disk.
    """

    from openbb_core.provider.utils.helpers import run_async

    from openbb_platform_api.utils.merge_widgets import (
        get_and_fix_widget_paths,
        has_additional_widgets,
    )
    from openbb_platform_api.utils.widgets import build_json

    global PATH_WIDGETS  # noqa: PLW0603

    if (
        FIRST_RUN is True
        and app
        and isinstance(app, FastAPI)
        and has_additional_widgets(app)
    ):
        PATH_WIDGETS = run_async(get_and_fix_widget_paths, app)

    if PATH_WIDGETS and (
        to_exclude := [p + "*" for p in PATH_WIDGETS if p.endswith("/")]
    ):
        # Router-attached widgets stake their own subtree; the auto
        # builder must skip those paths so we don't end up with two
        # widgets per route.
        widget_exclude_filter.extend(to_exclude)

    if editable is True:
        if widgets_path is None:
            python_path = Path(sys.executable)
            parent_path = (
                python_path.parent if os.name == "nt" else python_path.parents[1]
            )
            widgets_json_path = parent_path.joinpath("assets", "widgets.json").resolve()
        else:
            widgets_json_path = Path(widgets_path).absolute().resolve()

        json_exists = widgets_json_path.exists()

        if not json_exists:
            widgets_json_path.parent.mkdir(parents=True, exist_ok=True)
            _build = True
            json_exists = widgets_json_path.exists()

        existing_widgets_json: dict = {}

        if json_exists:
            with open(widgets_json_path, encoding="utf-8") as f:
                existing_widgets_json = json.load(f)

        _widgets_json = (
            existing_widgets_json
            if _build is False
            else build_json(_openapi, widget_exclude_filter)
        )

        if _build:
            diff = DeepDiff(existing_widgets_json, _widgets_json, ignore_order=True)
            merge_prompt = None
            if diff and json_exists:
                print("Differences found:", diff)  # noqa: T201
                merge_prompt = input(
                    "\nDo you want to overwrite the existing widgets.json configuration?"
                    "\nEnter 'n' to append existing with only new entries, or 'i' to ignore all changes. (y/n/i): "
                )
                if merge_prompt.lower().startswith("n"):
                    _widgets_json.update(existing_widgets_json)
                elif merge_prompt.lower().startswith("i"):
                    _widgets_json = existing_widgets_json

            if merge_prompt is None or not merge_prompt.lower().startswith("i"):
                try:
                    with open(widgets_json_path, "w", encoding="utf-8") as f:
                        json.dump(_widgets_json, f, ensure_ascii=False, indent=4)
                except Exception as e:
                    print(  # noqa: T201
                        f"Error writing widgets.json: {e}.  Loading from memory instead."
                    )
                    _widgets_json = (
                        existing_widgets_json
                        if existing_widgets_json
                        else build_json(_openapi, widget_exclude_filter)
                    )
    else:
        _widgets_json = build_json(_openapi, widget_exclude_filter)

        if PATH_WIDGETS:
            for k in PATH_WIDGETS:
                if k in widget_exclude_filter or k + "*" in widget_exclude_filter:
                    continue

                for widget_id, widget in PATH_WIDGETS[k].items():
                    if widget_id not in widget_exclude_filter:
                        _widgets_json[widget_id] = widget

    # Spec-driven launches stash a citation label on
    # ``app.state.openbb_spec_source`` (the spec file's name). Use it
    # to override every v4-platform default that ``build_json``
    # hardcoded — the ``["Custom"]`` source citation AND the
    # ``mcp_tool.mcp_server: "Open Data Platform"`` namespace.
    # Author-supplied overrides via ``widget_config`` are preserved.
    # Runs on both the initial startup build and the editable rebuild
    # path so the override is consistent across all surfaces.
    _apply_spec_defaults_override(_widgets_json, app)

    return _widgets_json


def _apply_spec_defaults_override(widgets_json: dict, app: FastAPI | None) -> None:
    """Replace v4-platform default values with spec-driven equivalents.

    When ``app.state.openbb_spec_source`` is set (the spec file's
    name, populated by ``args.parse_args`` for spec-driven launches),
    this helper rewrites three v4 launcher defaults on every widget
    that still carries them:

    * ``source: ["Custom"]`` → ``source: [spec_source]``
    * ``mcp_tool.mcp_server: "Open Data Platform"`` →
      ``mcp_tool.mcp_server: spec_source``
    * ``mcp_tool.tool_id: "<widget_id>"`` →
      ``mcp_tool.tool_id: "<spec_stem>__<widget_id>"``

    The first two are citation labels — straightforward replace.
    The third is namespacing: MCP tool IDs need to be globally
    unique across MCP servers a client connects to, so prefixing with
    the spec stem (filename minus extension) prevents collisions when
    multiple spec-driven launchers are wired up to the same client.
    The ``__`` separator is used because widget IDs can contain dots
    and underscores; ``__`` is unambiguous as a namespace boundary.

    All three defaults come from ``utils/widgets.build_json`` which
    was written for the v4 in-process Platform launch and assumes
    the canonical OpenBB MCP namespace. Spec-driven backends are
    their own MCP namespace — they should advertise themselves
    under the file they were generated from, not under the
    platform's.

    Author-supplied overrides (anything other than the literals
    above) are preserved untouched. The tool_id rewrite is gated on
    the v4 mcp_server default also being in place — if the author
    overrode ``mcp_server`` they own the whole ``mcp_tool`` block.
    No-op for non-spec-driven launches.
    """
    if app is None:
        return
    spec_source = getattr(app.state, "openbb_spec_source", None)
    if not spec_source:
        return
    # ``Path().stem`` strips the last extension only, so a filename
    # like ``my.app.spec`` becomes ``my.app`` (not ``my``). Matches
    # what most operators would call the namespace.
    spec_stem = Path(spec_source).stem or spec_source
    for widget in widgets_json.values():
        if widget.get("source") == ["Custom"]:
            widget["source"] = [spec_source]
        mcp_tool = widget.get("mcp_tool")
        if (
            isinstance(mcp_tool, dict)
            and mcp_tool.get("mcp_server") == "Open Data Platform"
        ):
            mcp_tool["mcp_server"] = spec_source
            tool_id = mcp_tool.get("tool_id")
            if isinstance(tool_id, str) and tool_id:
                mcp_tool["tool_id"] = f"{spec_stem}__{tool_id}"
