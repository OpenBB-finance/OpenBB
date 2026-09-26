"""Federal Reserve Bank of Kansas City regional router."""

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

router = Router(
    prefix="", description="Federal Reserve Bank of Kansas City indicators."
)


@router.command(
    model="FederalReserveKansasCityFinancialStress",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "KC Fed Financial Stress Index (KCFSI)",
        "description": "Monthly index of stress in the U.S. financial system; zero is"
        " the long-run average and positive values mark above-average stress.",
        "subCategory": "Financial & Policy",
        "gridData": {"w": 40, "h": 20},
        "data": {
            "table": {
                "showAll": True,
                "columnsDefs": [
                    {
                        "field": "date",
                        "headerName": "Date",
                        "cellDataType": "date",
                        "pinned": "left",
                        "sort": "desc",
                    },
                    {
                        "field": "kcfsi",
                        "headerName": "KCFSI",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                ],
            }
        },
    },
)
async def financial_stress_index(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Kansas City Financial Stress Index (KCFSI)."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveKansasCityRiskIndex",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
        APIEx(
            description="Get the weekly series.",
            parameters={"frequency": "weekly", "provider": "federal_reserve"},
        ),
    ],
    widget_config={
        "name": "KC Fed Risk-On/Risk-Off Index (RORO)",
        "description": "Composite measure of investor risk appetite and its four"
        " standardized components; positive values flag risk-off conditions.",
        "subCategory": "Financial & Policy",
        "gridData": {"w": 40, "h": 20},
        "data": {
            "table": {
                "showAll": True,
                "columnsDefs": [
                    {
                        "field": "date",
                        "headerName": "Date",
                        "cellDataType": "date",
                        "pinned": "left",
                        "sort": "desc",
                    },
                    {
                        "field": "roro",
                        "headerName": "RORO",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "spreads",
                        "headerName": "Credit Spreads",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "equities",
                        "headerName": "Equities",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "liquidity",
                        "headerName": "Liquidity",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "gold_currency",
                        "headerName": "Gold & Currency",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                ],
            }
        },
    },
)
async def risk_index(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Kansas City Risk-On/Risk-Off (RORO) Index."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveKansasCityPolicyRateUncertainty",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "KC Fed Policy Rate Uncertainty (KCPRU & KCPRS)",
        "description": "Daily option-implied uncertainty (KCPRU) about the expected"
        " federal funds rate path and the skew (KCPRS) of that distribution.",
        "subCategory": "Financial & Policy",
        "gridData": {"w": 40, "h": 20},
        "data": {
            "table": {
                "showAll": True,
                "columnsDefs": [
                    {
                        "field": "date",
                        "headerName": "Date",
                        "cellDataType": "date",
                        "pinned": "left",
                        "sort": "desc",
                    },
                    {
                        "field": "kcpru",
                        "headerName": "KCPRU",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "kcprs",
                        "headerName": "KCPRS",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                ],
            }
        },
    },
)
async def policy_rate_uncertainty(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Kansas City Policy Rate Uncertainty (KCPRU) and skew (KCPRS)."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveKansasCityNaturalRate",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "KC Fed Model-Based Natural Rates (r-star & u-star)",
        "description": "Monthly model-based estimates of the natural rate of interest"
        " (r-star) and the natural rate of unemployment (u-star), with 68% bands.",
        "subCategory": "Financial & Policy",
        "gridData": {"w": 40, "h": 20},
        "data": {
            "table": {
                "showAll": True,
                "columnsDefs": [
                    {
                        "field": "date",
                        "headerName": "Date",
                        "cellDataType": "date",
                        "pinned": "left",
                        "sort": "desc",
                    },
                    {
                        "field": "rstar",
                        "headerName": "r-star",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "rstar_lower",
                        "headerName": "r-star Lower",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "rstar_upper",
                        "headerName": "r-star Upper",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "ustar",
                        "headerName": "u-star",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "ustar_lower",
                        "headerName": "u-star Lower",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "ustar_upper",
                        "headerName": "u-star Upper",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                ],
            }
        },
    },
)
async def natural_rate(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Kansas City model-based natural rates of interest and unemployment."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveKansasCityDivisionalLmci",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
        APIEx(
            description="Get the momentum indicator.",
            parameters={"indicator": "momentum", "provider": "federal_reserve"},
        ),
    ],
    widget_config={
        "name": "KC Fed Divisional Labor Market Conditions (DIV-LMCI)",
        "description": "Labor market conditions index by the U.S. and the nine Census"
        " divisions, as either the level of activity or its momentum.",
        "subCategory": "Financial & Policy",
        "gridData": {"w": 40, "h": 20},
        "data": {
            "table": {
                "showAll": True,
                "columnsDefs": [
                    {
                        "field": "date",
                        "headerName": "Date",
                        "cellDataType": "date",
                        "pinned": "left",
                        "sort": "desc",
                    },
                ],
            }
        },
    },
)
async def divisional_lmci(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Kansas City Divisional Labor Market Conditions Indicators."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveKansasCityAgCreditSurvey",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
        APIEx(
            description="Get the farm credit condition diffusion indexes.",
            parameters={
                "table": "credit_conditions",
                "provider": "federal_reserve",
            },
        ),
    ],
    widget_config={
        "name": "KC Fed Tenth District Agricultural Credit Survey",
        "description": "Quarterly Tenth District farm credit diffusion indexes and"
        " farmland value changes by land class, by series.",
        "subCategory": "Agricultural Credit",
        "gridData": {"w": 40, "h": 20},
        "data": {
            "table": {
                "showAll": True,
                "columnsDefs": [
                    {
                        "field": "date",
                        "headerName": "Date",
                        "cellDataType": "date",
                        "pinned": "left",
                        "sort": "desc",
                    },
                ],
            }
        },
    },
)
async def ag_credit_survey(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Kansas City Fed Tenth District Agricultural Credit Survey."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveKansasCityAgRates",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
        APIEx(
            description="Get fixed real-estate loan rates.",
            parameters={
                "rate_type": "fixed",
                "loan_type": "real_estate",
                "provider": "federal_reserve",
            },
        ),
    ],
    widget_config={
        "name": "KC Fed Farm Loan Interest Rates",
        "description": "Quarterly average fixed and variable farm loan interest rates"
        " by state and district from the Tenth District credit survey.",
        "subCategory": "Agricultural Credit",
        "gridData": {"w": 40, "h": 20},
        "data": {
            "table": {
                "showAll": True,
                "columnsDefs": [
                    {
                        "field": "date",
                        "headerName": "Date",
                        "cellDataType": "date",
                        "pinned": "left",
                        "sort": "desc",
                    },
                ],
            }
        },
    },
)
async def ag_interest_rates(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Kansas City Fed farm loan interest rates by state and loan type."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveKansasCityAgFinance",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "KC Fed Ag Finance Databook",
        "description": "Quarterly history of agricultural lending at U.S. commercial"
        " banks from Call Reports: loan volumes, delinquency shares, and ratios.",
        "subCategory": "Agricultural Credit",
        "gridData": {"w": 40, "h": 20},
        "data": {
            "table": {
                "showAll": True,
                "columnsDefs": [
                    {
                        "field": "date",
                        "headerName": "Date",
                        "cellDataType": "date",
                        "pinned": "left",
                        "sort": "desc",
                    },
                ],
            }
        },
    },
)
async def ag_finance_databook(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Kansas City Fed Ag Finance Databook commercial-bank lending history."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveKansasCityAgTermsOfLending",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "KC Fed National Survey of Terms of Lending to Farmers",
        "description": "Quarterly non-real-estate farm loan volumes, sizes,"
        " maturities, and effective interest rates by loan purpose and size.",
        "subCategory": "Agricultural Credit",
        "gridData": {"w": 40, "h": 20},
        "data": {
            "table": {
                "showAll": True,
                "columnsDefs": [
                    {
                        "field": "date",
                        "headerName": "Date",
                        "cellDataType": "date",
                        "pinned": "left",
                        "sort": "desc",
                    },
                ],
            }
        },
    },
)
async def ag_terms_of_lending(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the National Survey of Terms of Lending to Farmers history."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveKansasCityAgDistrictSurveys",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
        APIEx(
            description="Filter to the Chicago district.",
            parameters={"district": "Chicago", "provider": "federal_reserve"},
        ),
    ],
    widget_config={
        "name": "Federal Reserve District Surveys of Ag Credit Conditions",
        "description": "Combined quarterly diffusion indexes of farm loan demand,"
        " repayment, fund availability, and farmland values across districts.",
        "subCategory": "Agricultural Credit",
        "gridData": {"w": 40, "h": 20},
        "data": {
            "table": {
                "showAll": True,
                "columnsDefs": [
                    {
                        "field": "date",
                        "headerName": "Date",
                        "cellDataType": "date",
                        "pinned": "left",
                        "sort": "desc",
                    },
                ],
            }
        },
    },
)
async def ag_district_surveys(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the combined Federal Reserve District Surveys of Ag Credit Conditions."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveKansasCityAgDatabookArchived",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
        APIEx(
            description="Get an interest-rate table from the archived databook.",
            parameters={"table": "afdr_b1", "provider": "federal_reserve"},
        ),
    ],
    widget_config={
        "name": "KC Fed Archived Ag Finance Databook",
        "description": "Discontinued pre-2018 databook: annual and quarterly series on"
        " farm debt, lending terms, and the condition of agricultural banks.",
        "subCategory": "Agricultural Credit",
        "gridData": {"w": 40, "h": 20},
        "data": {
            "table": {
                "showAll": True,
                "columnsDefs": [
                    {
                        "field": "date",
                        "headerName": "Date",
                        "cellDataType": "date",
                        "pinned": "left",
                        "sort": "desc",
                    },
                    {
                        "field": "frequency",
                        "headerName": "Frequency",
                    },
                    {
                        "field": "section",
                        "headerName": "Section",
                    },
                ],
            }
        },
    },
)
async def ag_databook_archived(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the archived (pre-2018) Kansas City Fed Ag Finance Databook tables."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveKansasCityPublications",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
)
async def publications(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Index the Kansas City Fed Agricultural Bulletin PDF archive."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveKansasCityPublicationSeries",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "Kansas City Fed Publication Series",
        "description": "The publication series supported by the Kansas City Fed"
        " publications catalog, with the document count in each.",
        "subCategory": "Publications & Reports",
        "gridData": {"w": 20, "h": 15},
        "data": {
            "table": {
                "showAll": True,
                "columnsDefs": [
                    {"field": "name", "headerName": "Series"},
                    {"field": "series", "headerName": "Slug"},
                    {"field": "count", "headerName": "Documents"},
                ],
            }
        },
    },
)
async def publication_series(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """List the supported Kansas City Fed publication series and their document counts."""
    return await OBBject.from_query(Query(**locals()))
