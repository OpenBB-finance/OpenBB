"""US Treasury Router."""

from pathlib import Path

from fastapi.responses import HTMLResponse
from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.example import APIEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query as OpenBBQuery
from openbb_core.app.router import Router

from openbb_government_us.treasury import FIXEDINCOME_INSTALLED

router = Router(
    prefix="",
    description="Data connector to the U.S. Treasury FiscalData API.",
)


async def get_us_treasury_apps_json() -> list[dict]:
    """Serve the US Treasury app definition for OpenBB Workspace."""
    import json

    apps_file = Path(__file__).parent / "assets" / "apps.json"
    try:
        with apps_file.open("r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:  # noqa: BLE001
        return []


router._api_router.add_api_route(
    path="/apps.json",
    endpoint=get_us_treasury_apps_json,
    methods=["GET"],
    include_in_schema=False,
)


@router.command(
    model="DebtToPenny",
    examples=[
        APIEx(parameters={"provider": "us_treasury"}),
        APIEx(
            description="Get the debt for a specific date range.",
            parameters={
                "start_date": "2025-01-01",
                "end_date": "2025-06-30",
                "provider": "us_treasury",
            },
        ),
    ],
)
async def debt_to_penny(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the total public debt outstanding, to the penny, for each business day."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="DailyTreasuryStatement",
    examples=[
        APIEx(parameters={"provider": "us_treasury"}),
        APIEx(
            description="Get the deposits and withdrawals of operating cash for June 2025.",
            parameters={
                "table": "deposits_withdrawals_operating_cash",
                "start_date": "2025-06-01",
                "end_date": "2025-06-30",
                "provider": "us_treasury",
            },
        ),
    ],
)
async def daily_statement(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get a table of the Daily Treasury Statement - cash and debt operations of the U.S. Treasury."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="UpcomingTreasuryAuctions",
    examples=[
        APIEx(parameters={"provider": "us_treasury"}),
        APIEx(
            description="Get only the upcoming bill auctions.",
            parameters={"security_type": "bill", "provider": "us_treasury"},
        ),
    ],
)
async def upcoming_auctions(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get marketable Treasury securities scheduled to be announced or auctioned in the coming week."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="TreasuryAuctionResults",
    examples=[
        APIEx(
            parameters={
                "start_date": "2025-01-01",
                "end_date": "2025-03-31",
                "provider": "us_treasury",
            }
        ),
        APIEx(
            description="Get all bond auctions since 2020.",
            parameters={
                "security_type": "bond",
                "start_date": "2020-01-01",
                "provider": "us_treasury",
            },
        ),
    ],
)
async def auction_results(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get announcements and results of marketable Treasury securities auctions back to 1979."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="TreasuryBillOfferings",
    examples=[
        APIEx(parameters={"provider": "us_treasury"}),
        APIEx(
            description="Get the weekly bill offerings issued during the first quarter of 2025.",
            parameters={
                "start_date": "2025-01-01",
                "end_date": "2025-03-31",
                "provider": "us_treasury",
            },
        ),
    ],
)
async def weekly_bill_offerings(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get regular weekly Treasury bill auction results from the Treasury Bulletin PDO-1 table."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="TreasuryBulletin",
    examples=[
        APIEx(parameters={"table": "ofs2", "provider": "us_treasury"}),
        APIEx(
            description="Get the distribution of federal securities by class of investors.",
            parameters={"table": "ofs1", "provider": "us_treasury"},
        ),
        APIEx(
            description="Get offerings of marketable securities other than regular weekly bills.",
            parameters={
                "table": "pdo2",
                "start_date": "2025-01-01",
                "provider": "us_treasury",
            },
        ),
    ],
)
async def bulletin(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get tables from the quarterly Treasury Bulletin - offerings, ownership distribution, currency and coin, foreign currency positions, the Exchange Stabilization Fund, and internal revenue receipts."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


if not FIXEDINCOME_INSTALLED:

    @router.command(
        model="TreasuryAuctions",
        examples=[
            APIEx(parameters={"provider": "us_treasury"}),
            APIEx(
                parameters={
                    "security_type": "Bill",
                    "start_date": "2022-01-01",
                    "end_date": "2023-01-01",
                    "provider": "us_treasury",
                }
            ),
        ],
    )
    async def treasury_auctions(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Government Treasury Auctions."""
        return await OBBject.from_query(OpenBBQuery(**locals()))

    @router.command(
        model="TreasuryPrices",
        examples=[
            APIEx(parameters={"provider": "us_treasury"}),
            APIEx(parameters={"date": "2019-02-05", "provider": "us_treasury"}),
        ],
    )
    async def treasury_prices(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Government Treasury Prices by date."""
        return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="UsSpendingAward",
    examples=[
        APIEx(
            description="Get the summary of an award by its usaspending.gov id.",
            parameters={
                "award_id": "CONT_IDV_15F06724A0000314_1549",
                "provider": "us_treasury",
            },
        ),
        APIEx(
            description="Drill into the subawards of an award.",
            parameters={
                "award_id": "CONT_IDV_15F06724A0000314_1549",
                "section": "subawards",
                "provider": "us_treasury",
            },
        ),
        APIEx(
            description="Get the orders placed against an indefinite delivery vehicle.",
            parameters={
                "award_id": "CONT_IDV_15F06724A0000314_1549",
                "section": "idv_children",
                "provider": "us_treasury",
            },
        ),
    ],
)
async def award(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Drill into a federal award from USAspending - its summary, transactions, subawards, federal accounts, funding, or the orders placed against a vehicle."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


SUBAWARD_PAGE_SIZE = 100

SUBAWARD_RENDER_CAP = 500


async def _award_subawards(award_id: str) -> list[dict]:
    """Fetch an award's subaward pages, up to the render cap."""
    from openbb_government_us.treasury.utils.usaspending import post_usaspending

    rows: list[dict] = []
    page = 1

    while len(rows) < SUBAWARD_RENDER_CAP:
        response = await post_usaspending(
            "subawards/",
            {"award_id": award_id, "page": page, "limit": SUBAWARD_PAGE_SIZE},
        )
        rows.extend(response.get("results") or [])

        if not (response.get("page_metadata") or {}).get("hasNext"):
            break

        page += 1

    return rows[:SUBAWARD_RENDER_CAP]


async def award_info(award_id: str, raw: bool = False):
    """Render one federal award's summary and subawards (OpenBB Workspace HTML widget)."""
    from fastapi.responses import HTMLResponse, JSONResponse

    from openbb_government_us.treasury.models.usaspending_award import (
        SUBJECT_KEY,
        UsSpendingAwardFetcher,
    )
    from openbb_government_us.treasury.utils.award_render import render_award_info

    query = UsSpendingAwardFetcher.transform_query(
        {"award_id": award_id, "section": "detail"}
    )
    rows = await UsSpendingAwardFetcher.aextract_data(query, None)
    records = [
        row.model_dump(mode="json")
        for row in UsSpendingAwardFetcher.transform_data(query, rows)
    ]
    detail = records[0] if records else {}
    total = detail.get("subaward_count")
    subawards: list[dict] = []

    if total is None or total > 0:
        sub_query = UsSpendingAwardFetcher.transform_query(
            {"award_id": award_id, "section": "subawards", "limit": SUBAWARD_PAGE_SIZE}
        )
        subawards = [
            row.model_dump(mode="json")
            for row in UsSpendingAwardFetcher.transform_data(
                sub_query,
                [
                    {**row, SUBJECT_KEY: award_id}
                    for row in await _award_subawards(award_id)
                ],
            )
        ]

    if raw:
        return JSONResponse(
            content=[
                *({"section": "detail", **record} for record in records),
                *({"section": "subawards", **record} for record in subawards),
            ]
        )

    return HTMLResponse(
        content=render_award_info(detail, subawards, total or len(subawards) or None)
    )


@router.command(
    model="UsSpendingExplorer",
    examples=[
        APIEx(
            description="Break all federal spending down by object class.",
            parameters={"provider": "us_treasury"},
        ),
        APIEx(
            description="Drill into the agencies acquiring assets.",
            parameters={
                "explorer_type": "agency",
                "scope": "object_class:30",
                "provider": "us_treasury",
            },
        ),
        APIEx(
            description="Drill into one agency's federal accounts for an object class.",
            parameters={
                "explorer_type": "federal_account",
                "scope": "agency:1173",
                "object_class": "30",
                "provider": "us_treasury",
            },
        ),
    ],
)
async def spending_explorer(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Explore all federal spending for a fiscal year, broken down by budget function, agency, federal account, program activity, object class, recipient, or award."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="UsSpendingRecipientSearch",
    examples=[
        APIEx(
            description="Find a recipient by name.",
            parameters={"keyword": "Lockheed Martin", "provider": "us_treasury"},
        ),
        APIEx(
            description="Look a recipient up by its UEI or legacy DUNS.",
            parameters={"keyword": "ZFN2JJXBLZT3", "provider": "us_treasury"},
        ),
        APIEx(
            description="Rank the largest grant recipients.",
            parameters={"award_type": "grants", "provider": "us_treasury"},
        ),
    ],
)
async def recipient_search(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Search every entity that has received federal contract or assistance money, by name, UEI, or legacy DUNS."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="UsSpendingRecipientAwards",
    examples=[
        APIEx(
            description="List a recipient's largest contracts.",
            parameters={
                "recipient_id": "b97d19b0-833c-8d8f-3a2c-157d04ea55ef-P",
                "provider": "us_treasury",
            },
        ),
        APIEx(
            description="List a recipient's grants.",
            parameters={
                "recipient_id": "ab4b0d9e-2a56-a67b-1fb7-b54a68b680ed-P",
                "award_group": "grants",
                "provider": "us_treasury",
            },
        ),
    ],
)
async def recipient_awards(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """List the federal awards belonging to one recipient, then drill into any award by its id."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


async def dts_amount_bases(table: str = "operating_cash_balance") -> list[dict]:
    """List the amount bases a Daily Treasury Statement table publishes."""
    from openbb_government_us.treasury.models.daily_treasury_statement import (
        ALL_BASES,
        VALUE_LABELS,
        amount_bases,
    )

    return [
        *(
            {"label": VALUE_LABELS[field], "value": VALUE_LABELS[field]}
            for field in amount_bases(table)
        ),
        {"label": "All bases", "value": ALL_BASES},
    ]


router._api_router.add_api_route(
    path="/dts_amount_bases",
    endpoint=dts_amount_bases,
    methods=["GET"],
    openapi_extra={"widget_config": {"exclude": True}},
)


async def explorer_types(
    budget_function: str | None = None,
    budget_subfunction: str | None = None,
    agency: str | None = None,
    federal_account: str | None = None,
    program_activity: str | None = None,
    object_class: str | None = None,
    recipient: str | None = None,
) -> list[dict]:
    """List the breakdowns that work for the current scope."""
    from openbb_government_us.treasury.utils.spending import explorer_type_options

    return explorer_type_options(
        any(
            (
                budget_function,
                budget_subfunction,
                agency,
                federal_account,
                program_activity,
                object_class,
                recipient,
            )
        )
    )


router._api_router.add_api_route(
    path="/explorer_types",
    endpoint=explorer_types,
    methods=["GET"],
    openapi_extra={"widget_config": {"exclude": True}},
)


async def spending_options(
    dimension: str = "agency", agency: str | None = None
) -> list[dict]:
    """List the selectable entries of one spending dimension."""
    from openbb_government_us.treasury.utils.spending import dimension_options

    return await dimension_options(dimension, agency)


router._api_router.add_api_route(
    path="/spending_options",
    endpoint=spending_options,
    methods=["GET"],
    openapi_extra={"widget_config": {"exclude": True}},
)


async def awarding_agencies() -> list[dict]:
    """List the top-tier awarding agencies."""
    from openbb_government_us.treasury.utils.spending import awarding_agency_options

    return await awarding_agency_options()


router._api_router.add_api_route(
    path="/awarding_agencies",
    endpoint=awarding_agencies,
    methods=["GET"],
    openapi_extra={"widget_config": {"exclude": True}},
)


async def def_codes() -> list[dict]:
    """List the Disaster Emergency Fund Codes as widget options."""
    from openbb_government_us.treasury.utils.award_filters import def_code_options

    return await def_code_options()


router._api_router.add_api_route(
    path="/def_codes",
    endpoint=def_codes,
    methods=["GET"],
    openapi_extra={"widget_config": {"exclude": True}},
)


async def dts_sub_tables(table: str = "operating_cash_balance") -> list[dict]:
    """List the sub-tables of one Daily Treasury Statement table."""
    from openbb_government_us.treasury.models.daily_treasury_statement import (
        sub_table_options,
    )

    return await sub_table_options(table)


router._api_router.add_api_route(
    path="/dts_sub_tables",
    endpoint=dts_sub_tables,
    methods=["GET"],
    openapi_extra={"widget_config": {"exclude": True}},
)


CHILD_RENDER_CAP = 200


async def recipient_info(recipient_id: str, year: str = "latest", raw: bool = False):
    """Render one federal recipient's profile (OpenBB Workspace HTML widget)."""
    import asyncio

    from fastapi.responses import HTMLResponse, JSONResponse
    from openbb_core.app.model.abstract.error import OpenBBError

    from openbb_government_us.treasury.utils.recipient import (
        EARLIEST_FISCAL_YEAR,
        TOP_CATEGORIES,
        get_children,
        get_profile,
        get_spending_over_time,
        get_top_category,
        resolve_window,
    )
    from openbb_government_us.treasury.utils.recipient_render import (
        recipient_rows,
        render_recipient_info,
    )

    period = (year or "").strip() or "latest"

    if period not in ("latest", "all") and (
        not period.isdigit() or int(period) < EARLIEST_FISCAL_YEAR
    ):
        raise OpenBBError(
            f"Invalid year: '{year}'. Use 'latest', 'all', or a fiscal year from"
            f" {EARLIEST_FISCAL_YEAR} onward."
        )

    profile = await get_profile(recipient_id, year=period)
    window = resolve_window(None, None)
    totals = await get_spending_over_time(recipient_id, "fiscal_year", window)
    denominator = sum(row.get("aggregated_amount") or 0 for row in totals) or None
    category_rows = await asyncio.gather(
        *(
            get_top_category(recipient_id, category, window)
            for category in TOP_CATEGORIES
        ),
        return_exceptions=True,
    )
    tops = {
        category: rows
        for category, rows in zip(TOP_CATEGORIES, category_rows, strict=True)
        if isinstance(rows, list) and rows
    }
    children: list[dict] = []

    if profile.get("recipient_level") == "P":
        children = await get_children(profile.get("uei") or profile.get("duns") or "")

    if raw:
        return JSONResponse(
            content=recipient_rows(profile, tops, children, denominator)
        )

    return HTMLResponse(
        content=render_recipient_info(
            profile,
            tops,
            children[:CHILD_RENDER_CAP],
            denominator,
            len(children),
        )
    )


router._api_router.add_api_route(
    path="/recipient_info",
    endpoint=recipient_info,
    methods=["GET"],
    response_class=HTMLResponse,
    openapi_extra={
        "widget_config": {
            "name": "Federal Recipient Info",
            "description": "Profile of a single federal award recipient from"
            " USAspending.gov - identity, location, totals, top awarding"
            " agencies, federal accounts, assistance listings, and geography,"
            " plus its child recipients.",
            "category": "Government",
            "subCategory": "Federal Awards",
            "source": ["US Treasury", "USAspending"],
            "type": "html",
            "raw": True,
            "widgetId": "ustreasury_recipient_info_us_treasury_obb",
            "gridData": {
                "w": 20,
                "h": 20,
            },
            "params": [
                {
                    "paramName": "recipient_id",
                    "label": "Recipient ID",
                    "description": "The recipient identifier, as returned by the"
                    " recipient search, e.g."
                    " 'ab4b0d9e-2a56-a67b-1fb7-b54a68b680ed-P'.",
                    "type": "text",
                    "value": "ab4b0d9e-2a56-a67b-1fb7-b54a68b680ed-P",
                    "show": True,
                },
                {
                    "paramName": "year",
                    "label": "Period",
                    "type": "text",
                    "value": "latest",
                    "show": True,
                    "multiSelect": False,
                    "options": [
                        {"label": "Trailing 12 months", "value": "latest"},
                        {"label": "All time", "value": "all"},
                    ],
                },
                {"paramName": "raw", "show": False},
            ],
            "refetchInterval": False,
        }
    },
)


router._api_router.add_api_route(
    path="/award_info",
    endpoint=award_info,
    methods=["GET"],
    response_class=HTMLResponse,
    openapi_extra={
        "widget_config": {
            "name": "Federal Award Info",
            "description": "Summary of a single federal contract or assistance"
            " award from USAspending.gov - amounts, period of performance,"
            " recipient, place of performance, agencies, and classification.",
            "category": "Government",
            "subCategory": "Federal Awards",
            "source": ["US Treasury", "USAspending"],
            "type": "html",
            "raw": True,
            "widgetId": "ustreasury_award_info_us_treasury_obb",
            "gridData": {
                "w": 20,
                "h": 20,
            },
            "params": [
                {
                    "paramName": "award_id",
                    "label": "Award ID",
                    "description": "The award identifier, as it appears in a"
                    " usaspending.gov/award/<id> URL.",
                    "type": "text",
                    "value": "CONT_IDV_15F06724A0000314_1549",
                    "show": True,
                },
                {"paramName": "raw", "show": False},
            ],
            "refetchInterval": False,
        }
    },
)


@router.command(
    model="UsSpendingAwardSearch",
    examples=[
        APIEx(
            description="Search the largest recent defense contracts.",
            parameters={
                "award_group": "contracts",
                "agency": "Department of Defense",
                "provider": "us_treasury",
            },
        ),
        APIEx(
            description="Find recent grants to a recipient by keyword.",
            parameters={
                "award_group": "grants",
                "recipient": "California",
                "keywords": "medicaid",
                "provider": "us_treasury",
            },
        ),
    ],
)
async def award_search(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Search federal contract and assistance awards from USAspending by agency, recipient, keyword, amount, and date, then drill into any award by its id."""
    return await OBBject.from_query(OpenBBQuery(**locals()))
