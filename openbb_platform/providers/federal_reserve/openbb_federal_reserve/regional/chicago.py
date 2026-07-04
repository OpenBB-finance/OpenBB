"""Federal Reserve Bank of Chicago regional router."""

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

router = Router(prefix="", description="Federal Reserve Bank of Chicago indicators.")


@router.command(
    model="FederalReserveChicagoNationalActivity",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "Chicago Fed National Activity Index (CFNAI)",
        "subCategory": "National Activity & Conditions",
        "description": "Monthly index of 85 indicators of U.S. national economic"
        " activity, with category contributions; zero is trend growth.",
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
                        "field": "cfnai",
                        "headerName": "CFNAI",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "cfnai_ma_3",
                        "headerName": "CFNAI MA3",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "diffusion",
                        "headerName": "Diffusion",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "production_income",
                        "headerName": "Production & Income",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "employment",
                        "headerName": "Employment",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "consumption_housing",
                        "headerName": "Consumption & Housing",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "sales_orders_inventories",
                        "headerName": "Sales, Orders & Inventories",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                ],
            }
        },
    },
)
async def national_activity(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Chicago Fed National Activity Index (CFNAI)."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveChicagoFinancialConditions",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "Chicago Fed National Financial Conditions Index (NFCI)",
        "subCategory": "National Activity & Conditions",
        "description": "Weekly index of U.S. financial conditions with the adjusted"
        " ANFCI and risk, credit, and leverage subindexes; zero is average.",
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
                        "field": "nfci",
                        "headerName": "NFCI",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "adjusted_nfci",
                        "headerName": "Adjusted NFCI",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "risk",
                        "headerName": "Risk",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "credit",
                        "headerName": "Credit",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "leverage",
                        "headerName": "Leverage",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "nonfinancial_leverage",
                        "headerName": "Nonfinancial Leverage",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                ],
            }
        },
    },
)
async def financial_conditions(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Chicago Fed National Financial Conditions Index (NFCI)."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveChicagoEconomicConditions",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "Chicago Fed Survey of Economic Conditions (CFSEC)",
        "subCategory": "National Activity & Conditions",
        "description": "Monthly Seventh District diffusion indexes of business"
        " activity, outlook, hiring, capital spending, and cost pressures.",
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
                        "field": "activity",
                        "headerName": "Activity",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "activity_manufacturing",
                        "headerName": "Activity (Manufacturing)",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "activity_nonmanufacturing",
                        "headerName": "Activity (Non-Manufacturing)",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "outlook",
                        "headerName": "Outlook",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "hiring",
                        "headerName": "Hiring",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "hiring_expectations",
                        "headerName": "Hiring Expectations",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "capital_spending_expectations",
                        "headerName": "Capital Spending Expectations",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "labor_costs",
                        "headerName": "Labor Costs",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "nonlabor_costs",
                        "headerName": "Non-Labor Costs",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                ],
            }
        },
    },
)
async def economic_conditions(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Chicago Fed Survey of Economic Conditions (CFSEC) diffusion indexes."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveChicagoRetailTrade",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
        APIEx(
            description="Get the monthly m/m percent changes with nowcast.",
            parameters={"figure": "monthly", "provider": "federal_reserve"},
        ),
    ],
    widget_config={
        "name": "Chicago Fed Advance Retail Trade Summary (CARTS)",
        "subCategory": "Retail & Labor",
        "description": "Weekly U.S. retail and food services sales index with monthly"
        " nowcasts and benchmark comparisons, one column per series.",
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
async def retail_trade(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Chicago Fed Advance Retail Trade Summary (CARTS)."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveChicagoLaborMarket",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "Chicago Fed Labor Market Indicators (CFLMI)",
        "subCategory": "Retail & Labor",
        "description": "Monthly U.S. labor-market flow rates and the real-time"
        " unemployment-rate nowcast, one column per indicator by vintage.",
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
                        "field": "release",
                        "headerName": "Release",
                    },
                ],
            }
        },
    },
)
async def labor_market(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Chicago Fed Labor Market Indicators (CFLMI)."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveChicagoFarmlandValues",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "Chicago Fed AgLetter Farmland Values",
        "subCategory": "Agriculture",
        "description": "Quarterly year-over-year percent changes in Seventh District"
        " farmland values, in aggregate and by state.",
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
                        "field": "year_over_year",
                        "headerName": "District (Y/Y)",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "illinois",
                        "headerName": "Illinois (Y/Y)",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "indiana",
                        "headerName": "Indiana (Y/Y)",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "iowa",
                        "headerName": "Iowa (Y/Y)",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "wisconsin",
                        "headerName": "Wisconsin (Y/Y)",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                ],
            }
        },
    },
)
async def farmland_values(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Chicago Fed AgLetter year-over-year farmland values."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveChicagoAgCredit",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "Chicago Fed AgLetter Agricultural Credit Conditions",
        "subCategory": "Agriculture",
        "description": "Quarterly Seventh District diffusion indexes of farm loan"
        " demand, fund availability, and repayment, with the loan-to-deposit ratio.",
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
                        "field": "loan_demand_index",
                        "headerName": "Loan Demand Index",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "fund_availability_index",
                        "headerName": "Fund Availability Index",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "loan_repayment_index",
                        "headerName": "Loan Repayment Index",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "loan_to_deposit_ratio",
                        "headerName": "Loan-to-Deposit Ratio",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                ],
            }
        },
    },
)
async def ag_credit_conditions(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Chicago Fed AgLetter agricultural credit conditions indexes."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveChicagoFarmLoanRates",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "Chicago Fed AgLetter New Farm Loan Interest Rates",
        "subCategory": "Agriculture",
        "description": "Quarterly average interest rates on new Seventh District farm"
        " operating, feeder cattle, and real estate loans, in percent.",
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
                        "field": "operating_loans",
                        "headerName": "Operating Loans",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "feeder_cattle_loans",
                        "headerName": "Feeder Cattle Loans",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "farm_real_estate_loans",
                        "headerName": "Farm Real Estate Loans",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                ],
            }
        },
    },
)
async def farm_loan_rates(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Chicago Fed AgLetter new farm loan interest rates."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveChicagoBraveButtersKelley",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "Chicago Fed Brave-Butters-Kelley Indexes (BBKI)",
        "subCategory": "National Activity & Conditions",
        "description": "Discontinued monthly decomposition of U.S. real GDP growth"
        " into trend, cyclical, and irregular components; last observation May 2022.",
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
                        "field": "coincident_index",
                        "headerName": "Coincident Index",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "leading_index",
                        "headerName": "Leading Index",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "cycle",
                        "headerName": "Cycle",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "cycle_leading",
                        "headerName": "Cycle (Leading)",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "cycle_lagging",
                        "headerName": "Cycle (Lagging)",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "trend",
                        "headerName": "Trend",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "irregular",
                        "headerName": "Irregular",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "monthly_gdp",
                        "headerName": "Monthly GDP",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                ],
            }
        },
    },
)
async def brave_butters_kelley(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Chicago Fed Brave-Butters-Kelley Indexes (BBKI, historical series)."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveChicagoMidwestEconomy",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "Chicago Fed Midwest Economy Index (MEI)",
        "subCategory": "National Activity & Conditions",
        "description": "Discontinued monthly index of Seventh District nonfarm"
        " business activity, by state and sector; last observation May 2021.",
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
                        "field": "mei",
                        "headerName": "MEI",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "illinois",
                        "headerName": "Illinois",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "indiana",
                        "headerName": "Indiana",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "iowa",
                        "headerName": "Iowa",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "michigan",
                        "headerName": "Michigan",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "wisconsin",
                        "headerName": "Wisconsin",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "regional",
                        "headerName": "Regional",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "manufacturing",
                        "headerName": "Manufacturing",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "construction",
                        "headerName": "Construction & Mining",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "services",
                        "headerName": "Services",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "consumer",
                        "headerName": "Consumer Spending",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                ],
            }
        },
    },
)
async def midwest_economy(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Chicago Fed Midwest Economy Index (MEI, historical series)."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveChicagoPublications",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
        APIEx(
            description="Index only the AgLetter series.",
            parameters={"series": "agletter", "provider": "federal_reserve"},
        ),
    ],
)
async def publications(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Index the Chicago Fed AgLetter, Fed Letter, EP, and Working Paper archives."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveChicagoPublicationSeries",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "Chicago Fed Publication Series",
        "description": "The publication series supported by the Chicago Fed"
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
    """List the supported Chicago Fed publication series and their document counts."""
    return await OBBject.from_query(Query(**locals()))
