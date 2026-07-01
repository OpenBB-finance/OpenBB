"""Federal Reserve Bank of New York regional router."""

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

from openbb_federal_reserve import ECONOMY_INSTALLED, FIXEDINCOME_INSTALLED
from openbb_federal_reserve.utils.primary_dealer_statistics import (
    POSITION_FIELD_TO_LABEL,
)

router = Router(prefix="", description="Federal Reserve Bank of New York indicators.")


@router.command(
    model="FederalReserveNewYorkSupplyChain",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "NY Fed Global Supply Chain Pressure Index (GSCPI)",
        "description": "Monthly composite of global supply chain conditions, in"
        " standard deviations from its historical average.",
        "subCategory": "Inflation",
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
                        "field": "gscpi",
                        "headerName": "GSCPI",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                ],
            }
        },
    },
)
async def supply_chain_pressure(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the New York Fed Global Supply Chain Pressure Index (GSCPI)."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveNewYorkCorporateDistress",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "NY Fed Corporate Bond Market Distress Index (CMDI)",
        "description": "Weekly index of distress in the U.S. corporate bond market,"
        " for the aggregate market and the IG and HY segments.",
        "subCategory": "Household & Credit",
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
                        "field": "market",
                        "headerName": "Market",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "investment_grade",
                        "headerName": "Investment Grade",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "high_yield",
                        "headerName": "High Yield",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                ],
            }
        },
    },
)
async def corporate_bond_distress(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the New York Fed Corporate Bond Market Distress Index (CMDI)."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveNewYorkConsumerExpectations",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
        APIEx(
            description="Get expected credit availability by respondent demographics.",
            parameters={
                "topic": "credit_availability",
                "provider": "federal_reserve",
            },
        ),
    ],
    widget_config={
        "name": "NY Fed Survey of Consumer Expectations (SCE)",
        "description": "Monthly Survey of Consumer Expectations results, one column"
        " per series, for the selected topic sheet.",
        "subCategory": "Consumer Surveys",
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
async def consumer_expectations(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the New York Fed Survey of Consumer Expectations across all topics."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveNewYorkBusinessLeaders",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "NY Fed Business Leaders Survey",
        "description": "Monthly diffusion indexes of current and six-month-ahead"
        " expected business activity for regional service-sector firms.",
        "subCategory": "Business Surveys",
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
                        "field": "current",
                        "headerName": "Current",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "expected",
                        "headerName": "Expected",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                ],
            }
        },
    },
)
async def business_leaders(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the New York Fed Business Leaders Survey diffusion indexes."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveNewYorkEmpireState",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
        APIEx(
            description="Get the up / down / same response shares behind each index.",
            parameters={
                "dataset": "seasonally_adjusted_all_series",
                "provider": "federal_reserve",
            },
        ),
    ],
    widget_config={
        "name": "NY Fed Empire State Manufacturing Survey",
        "description": "Monthly diffusion indexes and response shares for the Empire"
        " State Manufacturing Survey, one column per indicator-horizon-measure"
        " series.",
        "subCategory": "Business Surveys",
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
async def empire_state_manufacturing(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the New York Fed Empire State Manufacturing Survey diffusion indexes."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveNewYorkConsumerLaborMarket",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "NY Fed SCE Labor Market Survey — Reservation Wage",
        "description": "Average reservation wage from the triannual SCE Labor Market"
        " Survey, in U.S. dollars.",
        "subCategory": "Consumer Surveys",
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
                        "field": "average_reservation_wage",
                        "headerName": "Average Reservation Wage",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                ],
            }
        },
    },
)
async def consumer_labor_market(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the New York Fed SCE Labor Market Survey reservation wage."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveNewYorkConsumerHousing",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
        APIEx(
            description="Get expected mortgage rate perceptions by demographics.",
            parameters={
                "topic": "rate_perceptions_demo",
                "provider": "federal_reserve",
            },
        ),
    ],
    widget_config={
        "name": "NY Fed SCE Housing Survey",
        "description": "Annual SCE Housing Survey results, one column per series, for"
        " the selected topic sheet.",
        "subCategory": "Consumer Surveys",
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
async def consumer_housing(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the New York Fed SCE Housing Survey across all topics."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveNewYorkConsumerCreditAccess",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
        APIEx(
            description="Get the breakdown by age and credit-score group.",
            parameters={"breakdown": "demographics", "provider": "federal_reserve"},
        ),
    ],
    widget_config={
        "name": "NY Fed SCE Credit Access Survey",
        "description": "Triannual SCE Credit Access Survey application, acceptance,"
        " rejection, and expectation series, one column per series, by respondent"
        " group and category.",
        "subCategory": "Consumer Surveys",
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
                        "field": "group",
                        "headerName": "Group",
                    },
                    {
                        "field": "category",
                        "headerName": "Category",
                    },
                ],
            }
        },
    },
)
async def consumer_credit_access(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the New York Fed SCE Credit Access Survey across all metrics."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveNewYorkHouseholdDebt",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
        APIEx(
            description="Get the by-state composition of debt balance per capita.",
            parameters={
                "table": "composition_of_debt_balance_per_capita_by_state",
                "provider": "federal_reserve",
            },
        ),
    ],
    widget_config={
        "name": "NY Fed Household Debt and Credit",
        "description": "Quarterly Report on Household Debt and Credit, one column per"
        " series, for the selected report table.",
        "subCategory": "Household & Credit",
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
async def household_debt(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the New York Fed total household debt balance by category."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveNewYorkCoreTrendInflation",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "NY Fed Multivariate Core Trend (MCT) Inflation",
        "description": "Monthly model-based estimate of core PCE trend inflation, with"
        " uncertainty bands and the sector decomposition, in annualized percent.",
        "subCategory": "Inflation",
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
                        "field": "mct",
                        "headerName": "MCT",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "mct_upper",
                        "headerName": "MCT Upper",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "mct_upper_2",
                        "headerName": "MCT Upper (Outer)",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "mct_lower",
                        "headerName": "MCT Lower",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "headline_pce",
                        "headerName": "Headline PCE",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "core_pce",
                        "headerName": "Core PCE",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "goods",
                        "headerName": "Goods",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "services_ex_housing",
                        "headerName": "Services ex-Housing",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "housing",
                        "headerName": "Housing",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "goods_common",
                        "headerName": "Goods (Common)",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "goods_sector_specific",
                        "headerName": "Goods (Sector-Specific)",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "services_ex_housing_common",
                        "headerName": "Services ex-Housing (Common)",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "services_ex_housing_sector_specific",
                        "headerName": "Services ex-Housing (Sector-Specific)",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "housing_common",
                        "headerName": "Housing (Common)",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "housing_sector_specific",
                        "headerName": "Housing (Sector-Specific)",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                ],
            }
        },
    },
)
async def core_trend_inflation(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the New York Fed Multivariate Core Trend (MCT) inflation estimate."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveNewYorkEmpireReports",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "NY Fed Empire State Survey Report Index",
        "description": "Catalog of published Empire State Manufacturing Survey monthly"
        " report PDFs, with a direct link to each document.",
        "subCategory": "Business Surveys",
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
                    {"field": "period", "headerName": "Period"},
                    {"field": "url", "headerName": "URL"},
                ],
            }
        },
    },
)
async def empire_state_reports(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Index the New York Fed Empire State Survey monthly report PDF archive."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveNewYorkMarketExpectations",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
        APIEx(
            description="Index only the results reports.",
            parameters={"kind": "results", "provider": "federal_reserve"},
        ),
    ],
    widget_config={
        "name": "NY Fed Survey of Market Expectations Index",
        "description": "Catalog of the pre-FOMC Surveys of Primary Dealers and Market"
        " Participants, with a direct link to each PDF.",
        "subCategory": "Rates & Markets",
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
                    {"field": "kind", "headerName": "Kind"},
                    {"field": "subtype", "headerName": "Panel"},
                    {"field": "title", "headerName": "Title"},
                    {"field": "url", "headerName": "URL"},
                ],
            }
        },
    },
)
async def market_expectations(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Index the New York Fed Survey of Market Expectations PDF archive."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveNewYorkPublications",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
        APIEx(
            description="Filter the catalog to one report series.",
            parameters={"series": "empire_state_report", "provider": "federal_reserve"},
        ),
    ],
)
async def publications(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Index the New York Fed report PDF archives in a multi-file viewer."""
    return await OBBject.from_query(Query(**locals()))


if not FIXEDINCOME_INSTALLED:

    @router.command(
        model="FederalReserveSOFR",
        examples=[APIEx(parameters={"provider": "federal_reserve"})],
        widget_config={
            "name": "Secured Overnight Financing Rate (SOFR)",
            "description": "Daily SOFR benchmark rate and its percentile"
            " distribution, in percent, with transaction volume.",
            "subCategory": "Rates & Markets",
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
                            "field": "rate",
                            "headerName": "Rate",
                            "cellDataType": "number",
                            "formatterFn": "percent",
                        },
                        {
                            "field": "percentile_1",
                            "headerName": "1st Percentile",
                            "cellDataType": "number",
                            "formatterFn": "percent",
                        },
                        {
                            "field": "percentile_25",
                            "headerName": "25th Percentile",
                            "cellDataType": "number",
                            "formatterFn": "percent",
                        },
                        {
                            "field": "percentile_75",
                            "headerName": "75th Percentile",
                            "cellDataType": "number",
                            "formatterFn": "percent",
                        },
                        {
                            "field": "percentile_99",
                            "headerName": "99th Percentile",
                            "cellDataType": "number",
                            "formatterFn": "percent",
                        },
                        {
                            "field": "volume",
                            "headerName": "Volume",
                            "cellDataType": "number",
                            "formatterFn": "none",
                        },
                    ],
                }
            },
        },
    )
    async def sofr(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Get the Secured Overnight Financing Rate (SOFR)."""
        return await OBBject.from_query(Query(**locals()))

    @router.command(
        model="FederalReserveFederalFundsRate",
        examples=[APIEx(parameters={"provider": "federal_reserve"})],
        widget_config={
            "name": "Effective Federal Funds Rate (EFFR)",
            "description": "Daily effective federal funds rate, target range, and"
            " percentile distribution, in percent, with transaction volume.",
            "subCategory": "Rates & Markets",
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
                            "field": "rate",
                            "headerName": "Rate",
                            "cellDataType": "number",
                            "formatterFn": "percent",
                        },
                        {
                            "field": "target_range_upper",
                            "headerName": "Target Range Upper",
                            "cellDataType": "number",
                            "formatterFn": "percent",
                        },
                        {
                            "field": "target_range_lower",
                            "headerName": "Target Range Lower",
                            "cellDataType": "number",
                            "formatterFn": "percent",
                        },
                        {
                            "field": "percentile_1",
                            "headerName": "1st Percentile",
                            "cellDataType": "number",
                            "formatterFn": "percent",
                        },
                        {
                            "field": "percentile_25",
                            "headerName": "25th Percentile",
                            "cellDataType": "number",
                            "formatterFn": "percent",
                        },
                        {
                            "field": "percentile_75",
                            "headerName": "75th Percentile",
                            "cellDataType": "number",
                            "formatterFn": "percent",
                        },
                        {
                            "field": "percentile_99",
                            "headerName": "99th Percentile",
                            "cellDataType": "number",
                            "formatterFn": "percent",
                        },
                        {
                            "field": "volume",
                            "headerName": "Volume",
                            "cellDataType": "number",
                            "formatterFn": "none",
                        },
                        {
                            "field": "intraday_low",
                            "headerName": "Intraday Low",
                            "cellDataType": "number",
                            "formatterFn": "percent",
                        },
                        {
                            "field": "intraday_high",
                            "headerName": "Intraday High",
                            "cellDataType": "number",
                            "formatterFn": "percent",
                        },
                        {
                            "field": "standard_deviation",
                            "headerName": "Standard Deviation",
                            "cellDataType": "number",
                            "formatterFn": "percent",
                        },
                        {
                            "field": "revision_indicator",
                            "headerName": "Revision Indicator",
                        },
                    ],
                }
            },
        },
    )
    async def effr(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Get Effective Federal Funds Rate data."""
        return await OBBject.from_query(Query(**locals()))

    @router.command(
        model="FederalReserveOvernightBankFundingRate",
        examples=[APIEx(parameters={"provider": "federal_reserve"})],
        widget_config={
            "name": "Overnight Bank Funding Rate (OBFR)",
            "description": "Daily OBFR benchmark rate and its percentile"
            " distribution, in percent, with transaction volume.",
            "subCategory": "Rates & Markets",
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
                            "field": "rate",
                            "headerName": "Rate",
                            "cellDataType": "number",
                            "formatterFn": "percent",
                        },
                        {
                            "field": "percentile_1",
                            "headerName": "1st Percentile",
                            "cellDataType": "number",
                            "formatterFn": "percent",
                        },
                        {
                            "field": "percentile_25",
                            "headerName": "25th Percentile",
                            "cellDataType": "number",
                            "formatterFn": "percent",
                        },
                        {
                            "field": "percentile_75",
                            "headerName": "75th Percentile",
                            "cellDataType": "number",
                            "formatterFn": "percent",
                        },
                        {
                            "field": "percentile_99",
                            "headerName": "99th Percentile",
                            "cellDataType": "number",
                            "formatterFn": "percent",
                        },
                        {
                            "field": "volume",
                            "headerName": "Volume",
                            "cellDataType": "number",
                            "formatterFn": "none",
                        },
                        {
                            "field": "revision_indicator",
                            "headerName": "Revision Indicator",
                        },
                    ],
                }
            },
        },
    )
    async def overnight_bank_funding(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Get the Overnight Bank Funding Rate (OBFR)."""
        return await OBBject.from_query(Query(**locals()))


if not ECONOMY_INSTALLED:

    @router.command(
        model="FederalReserveCentralBankHoldings",
        examples=[
            APIEx(
                description="The default is the latest Treasury securities held by the Federal Reserve.",
                parameters={"provider": "federal_reserve"},
            ),
            APIEx(
                description="Get historical summaries of the Fed's holdings.",
                parameters={"provider": "federal_reserve", "summary": True},
            ),
            APIEx(
                description="Get the balance sheet holdings as-of a historical date.",
                parameters={"provider": "federal_reserve", "date": "2019-05-21"},
            ),
            APIEx(
                description="Use the `holding_type` parameter to select Agency securities,"
                + " or specific categories or Treasury securities.",
                parameters={
                    "provider": "federal_reserve",
                    "holding_type": "agency_debts",
                },
            ),
        ],
        widget_config={
            "name": "System Open Market Account (SOMA) Holdings",
            "description": "Treasury and Agency securities held by the Federal Reserve"
            " and managed by the New York Fed, in USD.",
            "subCategory": "Rates & Markets",
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
                            "field": "security_type",
                            "headerName": "Security Type",
                        },
                        {
                            "field": "cusip",
                            "headerName": "CUSIP",
                        },
                        {
                            "field": "description",
                            "headerName": "Description",
                        },
                        {
                            "field": "term",
                            "headerName": "Term",
                        },
                        {
                            "field": "issuer",
                            "headerName": "Issuer",
                        },
                        {
                            "field": "maturity_date",
                            "headerName": "Maturity Date",
                            "cellDataType": "date",
                        },
                        {
                            "field": "par_value",
                            "headerName": "Par Value",
                            "cellDataType": "number",
                            "formatterFn": "int",
                        },
                        {
                            "field": "face_value",
                            "headerName": "Face Value",
                            "cellDataType": "number",
                            "formatterFn": "int",
                        },
                        {
                            "field": "coupon",
                            "headerName": "Coupon",
                            "cellDataType": "number",
                            "formatterFn": "percent",
                        },
                        {
                            "field": "spread",
                            "headerName": "Spread",
                            "cellDataType": "number",
                            "formatterFn": "percent",
                        },
                        {
                            "field": "percent_outstanding",
                            "headerName": "Percent Outstanding",
                            "cellDataType": "number",
                            "formatterFn": "percent",
                        },
                        {
                            "field": "change_prior_week",
                            "headerName": "Change Prior Week",
                            "cellDataType": "number",
                            "formatterFn": "int",
                        },
                        {
                            "field": "change_prior_year",
                            "headerName": "Change Prior Year",
                            "cellDataType": "number",
                            "formatterFn": "int",
                        },
                        {
                            "field": "bills",
                            "headerName": "Bills",
                            "cellDataType": "number",
                            "formatterFn": "int",
                        },
                        {
                            "field": "notes_and_bonds",
                            "headerName": "Notes & Bonds",
                            "cellDataType": "number",
                            "formatterFn": "int",
                        },
                        {
                            "field": "frn",
                            "headerName": "FRN",
                            "cellDataType": "number",
                            "formatterFn": "int",
                        },
                        {
                            "field": "tips",
                            "headerName": "TIPS",
                            "cellDataType": "number",
                            "formatterFn": "int",
                        },
                        {
                            "field": "tips_inflation_compensation",
                            "headerName": "TIPS Inflation Compensation",
                            "cellDataType": "number",
                            "formatterFn": "int",
                        },
                        {
                            "field": "mbs",
                            "headerName": "MBS",
                            "cellDataType": "number",
                            "formatterFn": "int",
                        },
                        {
                            "field": "cmbs",
                            "headerName": "CMBS",
                            "cellDataType": "number",
                            "formatterFn": "int",
                        },
                        {
                            "field": "agencies",
                            "headerName": "Agencies",
                            "cellDataType": "number",
                            "formatterFn": "int",
                        },
                        {
                            "field": "total",
                            "headerName": "Total",
                            "cellDataType": "number",
                            "formatterFn": "int",
                        },
                    ],
                }
            },
        },
    )
    async def central_bank_holdings(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Get the System Open Market Account (SOMA) balance sheet holdings."""
        return await OBBject.from_query(Query(**locals()))

    @router.command(
        model="FederalReservePrimaryDealerPositioning",
        examples=[
            APIEx(parameters={"provider": "federal_reserve"}),
            APIEx(parameters={"category": "abs", "provider": "federal_reserve"}),
        ],
        widget_config={
            "name": "Primary Dealer Positioning",
            "description": "Weekly net positions (long minus short) reported by primary"
            " dealers, by series, in millions of USD.",
            "subCategory": "Rates & Markets",
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
                        *[
                            {
                                "field": field,
                                "headerName": POSITION_FIELD_TO_LABEL[field],
                                "cellDataType": "number",
                                "formatterFn": "int",
                            }
                            for field in POSITION_FIELD_TO_LABEL
                        ],
                    ],
                }
            },
        },
    )
    async def primary_dealer_positioning(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Get Primary dealer positioning statistics."""
        return await OBBject.from_query(Query(**locals()))

    @router.command(
        model="FederalReservePrimaryDealerFails",
        examples=[
            APIEx(parameters={"provider": "federal_reserve"}),
            APIEx(
                description="Transform the data to be percentage totals by asset class.",
                parameters={"provider": "federal_reserve", "unit": "percent"},
            ),
        ],
        widget_config={
            "name": "Primary Dealer Fails to Deliver and Receive",
            "description": "Weekly settlement fails reported by primary dealers, by"
            " series, in millions of USD or as a share of total fails.",
            "subCategory": "Rates & Markets",
            "gridData": {"w": 40, "h": 20},
            "data": {
                "table": {
                    "showAll": True,
                    "columnsDefs": [
                        {
                            "field": "date",
                            "headerName": "Date",
                            "cellDataType": "date",
                            "chartDataType": "time",
                            "pinned": "left",
                            "sort": "desc",
                        },
                        *[
                            {
                                "field": title,
                                "headerName": title,
                                "cellDataType": "number",
                                "chartDataType": "series",
                            }
                            for title in (
                                "FTD Treasury Securities (Ex-TIPS)",
                                "FTD TIPS",
                                "FTD Agency and GSE Securities (Ex-MBS)",
                                "FTD Agency and GSE MBS",
                                "FTD Other MBS",
                                "FTD Corporate Securities",
                                "FTD Total",
                                "FTR Treasury Securities (Ex-TIPS)",
                                "FTR TIPS",
                                "FTR Agency and GSE Securities (Ex-MBS)",
                                "FTR Agency and GSE MBS",
                                "FTR Other MBS",
                                "FTR Corporate Securities",
                                "FTR Total",
                            )
                        ],
                    ],
                }
            },
        },
    )
    async def primary_dealer_fails(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Get Primary Dealer Statistics for Fails to Deliver and Fails to Receive."""
        return await OBBject.from_query(Query(**locals()))
