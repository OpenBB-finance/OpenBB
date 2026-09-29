"""BLS Core (Series, Search, Calendar) sub-router."""

from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.example import APIEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query as OBBQuery
from openbb_core.app.router import Router

from openbb_bls import ECONOMY_INSTALLED

router = Router(prefix="", description="BLS Core (Series, Search, Calendar) router.")

# Memoized ``[{label, value}]`` series options, keyed by (cache singleton id,
# category) so the picker is parameterized per category and rebuilds when the
# cache is (re)loaded. Scoping by category keeps each dropdown small enough to
# fetch and search client-side instead of shipping the full ~1.1M universe.
_SYMBOL_CHOICES_CACHE: dict[tuple[int, str], list] = {}


def _category_series_choices(category: str) -> list:
    """Build ``[{label, value}]`` for every series in one category.

    The Series widget's ``symbol`` picker points here with
    ``optionsParams={"category": "$category"}``; the Search widget's cell-click
    ``groupBy`` then resolves against this same category-scoped option set.
    Current (still-updated) series are ordered first.
    """
    from openbb_bls.models.search import _fill_titles, _rank_by_recency
    from openbb_bls.utils.metadata import BlsMetadata

    meta = BlsMetadata()
    key = (id(meta), category)
    cached = _SYMBOL_CHOICES_CACHE.get(key)
    if cached is not None:
        return cached

    try:
        df = _rank_by_recency(_fill_titles(meta.get_series(category)))
    except KeyError:
        return []

    options = [
        {
            "label": f"{sym} — {title}" if title else str(sym),
            "value": sym,
        }
        for sym, title in zip(df["series_id"].tolist(), df["series_title"].tolist())
    ]
    # Keep only this build (cache invalidates when the singleton is replaced).
    for stale in [k for k in _SYMBOL_CHOICES_CACHE if k[0] != id(meta)]:
        del _SYMBOL_CHOICES_CACHE[stale]
    _SYMBOL_CHOICES_CACHE[key] = options
    return options


@router.api_router.get("/series/symbol_choices", include_in_schema=False)
async def series_symbol_choices(category: str = "cpi") -> list:
    """Return ``[{label, value}]`` series for *category* (the Series symbol picker)."""
    return _category_series_choices(category)


if not ECONOMY_INSTALLED:

    @router.command(
        model="BlsSearch",
        examples=[
            APIEx(
                description="Search the CPI category for series matching a query.",
                parameters={"provider": "bls", "category": "cpi", "query": "urban"},
            ),
            APIEx(
                description="List every series in the JOLTS category.",
                parameters={"provider": "bls", "category": "jolts"},
            ),
        ],
    )
    async def search(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Search the BLS series catalog by category, keyword, or code."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="BlsSeries",
        examples=[
            APIEx(
                description="Fetch a single series by symbol from the BLS API.",
                parameters={"provider": "bls", "symbol": "CUUR0000SA0"},
            ),
            APIEx(
                description="Fetch multiple series with calculations enabled.",
                parameters={
                    "provider": "bls",
                    "symbol": "CUUR0000SA0,WPUFD4",
                    "calculations": True,
                },
            ),
        ],
    )
    async def series(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Fetch BLS time series data by series identifier."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="BlsEconomicCalendar",
        examples=[
            APIEx(
                description="Current-month BLS release schedule.",
                parameters={"provider": "bls"},
            ),
            APIEx(
                description="Filter releases to a specific name across a window.",
                parameters={
                    "provider": "bls",
                    "start_date": "2026-04-01",
                    "end_date": "2026-06-30",
                    "release": "Employment Situation",
                },
            ),
        ],
    )
    async def calendar(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """BLS Release Calendar."""
        return await OBBject.from_query(OBBQuery(**locals()))
