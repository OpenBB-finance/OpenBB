"""Commodity Futures Trading Commission (CFTC) Router."""

# pylint: disable=W0212,W0613

from typing import Any

from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.example import APIEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query
from openbb_core.app.router import Router

router = Router(prefix="")
COT_CHOICES: list[dict[str, str | dict[str, str | None]]] = []


async def build_choices():
    """Build the choices for Workspace."""
    # pylint: disable=import-outside-toplevel
    from openbb_cftc.models.cot_search import CftcCotSearchFetcher

    contracts = await CftcCotSearchFetcher.fetch_data({}, {})
    choices: list[dict[str, str | dict[str, str | None]]] = []

    for d in contracts:
        choice: dict[str, str | dict[str, str | None]] = {
            "label": d.name.strip(),  # type: ignore
            "value": d.code.strip(),  # type: ignore
            "extraInfo": {"description": f"{d.subcategory.strip()}  | {d.code.strip()}", "rightOfDescription": ""},  # type: ignore
        }
        choices.append(choice)

    global COT_CHOICES  # noqa: PLW0603  # pylint: disable=W0603

    COT_CHOICES = choices


router.api_router.add_event_handler("startup", build_choices)


async def get_cot_choices() -> list[dict[str, str | dict[str, str | None]]]:
    """Get the choices for the COT command in Workspace."""
    return COT_CHOICES


router._api_router.add_api_route(
    path="/get_cot_choices",
    endpoint=get_cot_choices,
    methods=["GET"],
    include_in_schema=False,
)


@router.command(
    model="COTSearch",
    examples=[
        APIEx(parameters={"provider": "cftc"}),
        APIEx(parameters={"query": "gold", "provider": "cftc"}),
    ],
    widget_config={
        "name": "Commitment of Traders Search",
        "description": "Search for CFTC Commitment of Traders (COT) report series.",
        "category": "CFTC",
        "subCategory": "COT",
        "refetchInterval": False,
    },
)
async def cot_search(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Search current Commitment of Traders Reports."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="COT",
    examples=[
        APIEx(parameters={"provider": "ctfc"}),
        APIEx(
            description="Get the latest report for all items classified as, GOLD.",
            parameters={"code": "CFTC_088691", "limit": 1, "provider": "cftc"},
        ),
        APIEx(
            description="Get the report for futures only.",
            parameters={
                "code": "CFTC_088691",
                "futures_only": True,
                "limit": 1,
                "provider": "cftc",
            },
        ),
        APIEx(
            description="Filter the report down to a specific section.",
            parameters={
                "code": "CFTC_088691",
                "futures_only": True,
                "measure": "changes",
                "limit": 1,
                "provider": "cftc",
            },
        ),
    ],
    widget_config={
        "name": "Commitment of Traders",
        "description": "CFTC Commitment of Traders (COT) reports.",
        "category": "CFTC",
        "subCategory": "COT",
        "refetchInterval": False,
    },
)
async def cot(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get Commitment of Traders Reports."""
    return await OBBject.from_query(Query(**locals()))


async def get_cftc_apps_json() -> list[dict[str, Any]]:
    """Get the IMF apps.json file.

    This endpoint serves the apps.json file containing OpenBB Workspace app configurations.
    It is automatically merged with any existing apps.json files in the Workspace and API.

    Returns
    -------
    list[dict[str, Any]]
        A list of OpenBB Workspace app configurations.
    """
    # pylint: disable=import-outside-toplevel
    import json
    from pathlib import Path

    apps_file = Path(__file__).parent / "apps.json"

    try:
        with apps_file.open("r", encoding="utf-8") as f:
            apps_json = json.load(f)
            return apps_json
    except Exception:
        return []


router._api_router.add_api_route(
    path="/apps.json",
    endpoint=get_cftc_apps_json,
    methods=["GET"],
    include_in_schema=False,
)
