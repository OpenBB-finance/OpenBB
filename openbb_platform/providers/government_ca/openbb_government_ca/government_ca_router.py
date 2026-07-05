"""Top-level router for ``openbb-government-ca``."""

from typing import Annotated

from fastapi import Query
from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.example import APIEx, PythonEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query as OBBQuery
from openbb_core.app.router import Router
from openbb_core.app.service.system_service import SystemService

from openbb_government_ca.utils.metadata import GovernmentCaMetadataDependency

router = Router(prefix="", description="Government of Canada router")
api_prefix = SystemService().system_settings.api_settings.prefix


@router.command(
    model="AvailableIndicators",
    examples=[
        APIEx(parameters={"provider": "government_ca"}),
        APIEx(
            description="Search by series label substring.",
            parameters={"provider": "government_ca", "query": "GDP"},
        ),
        APIEx(
            description="List every series in a cube.",
            parameters={"provider": "government_ca", "cube_pid": "10100139"},
        ),
    ],
)
async def available_indicators(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """List available StatsCan indicators (pure metadata, no observation values)."""
    return await OBBject.from_query(OBBQuery(**locals()))


@router.command(
    path="/list_cube_choices",
    response_model=list[dict[str, str]],
    examples=[
        APIEx(
            description="List all cubes in the SDMX catalog",
            api=f"{api_prefix}/government_ca/list_cube_choices",
            parameters={"provider": "government_ca"},
        ),
        APIEx(
            description="Search cubes by title substring",
            api=f"{api_prefix}/government_ca/list_cube_choices?query=GDP",
            parameters={"provider": "government_ca", "query": "GDP"},
        ),
        PythonEx(
            description="List cubes via the Python API",
            code=[
                "obb.government_ca.list_cube_choices(query='GDP')",
            ],
        ),
    ],
)
def list_cube_choices(
    metadata: GovernmentCaMetadataDependency,
    query: Annotated[
        str | None,
        Query(description="Case-insensitive substring filter on cube title"),
    ] = None,
) -> OBBject[list[dict[str, str]]]:
    """Return ``[{pid, title_en, subject_code, frequency_code}]`` for every cube.

    Pure metadata — no observation values. Use this to populate UI
    dropdowns and ``Literal`` parameter choices for the
    ``economic_indicators`` fetcher.
    """
    from openbb_government_ca.statscan.utils import get_catalog, list_cubes

    cache = metadata.statscan
    if not get_catalog(cache).get("cubes"):
        return OBBject(results=[])

    needle = (query or "").lower().strip()
    results: list[dict[str, str]] = []
    for cube in list_cubes(cache):
        title = cube.get("title_en", "")
        if needle and needle not in title.lower():
            continue
        results.append(
            {
                "pid": cube.get("pid", ""),
                "title_en": title,
                "subject_code": cube.get("subject_code", ""),
                "frequency_code": cube.get("frequency_code", ""),
            }
        )
    return OBBject(results=results)


@router.command(
    path="/list_subject_choices",
    response_model=list[dict[str, str]],
    examples=[
        APIEx(
            description="List all subjects in the SDMX catalog",
            api=f"{api_prefix}/government_ca/list_subject_choices",
            parameters={"provider": "government_ca"},
        ),
    ],
)
def list_subject_choices(
    metadata: GovernmentCaMetadataDependency,
) -> OBBject[list[dict[str, str]]]:
    """Return ``[{subject_code, label}]`` for every subject in the catalog."""
    from openbb_government_ca.statscan.utils import list_subjects

    subjects = list_subjects(metadata.statscan)
    return OBBject(
        results=[{"subject_code": k, "label": v} for k, v in subjects.items()]
    )
