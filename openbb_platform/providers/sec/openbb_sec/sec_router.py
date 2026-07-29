"""SEC Router."""

from typing import Annotated

from fastapi import (
    Query as FastAPIQuery,
)
from openbb_core.app.model.aggrid import AgGridRowsRequest
from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.example import APIEx, PythonEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query
from openbb_core.app.router import Router
from pydantic import BaseModel

router = Router(
    prefix="",
    description="U.S. Securities and Exchange Commission (SEC) public data.",
)


@router.command(
    model="SecFiling",
    examples=[
        APIEx(
            parameters={
                "url": "https://www.sec.gov/Archives/edgar/data/317540/000119312524076556/d645509ddef14a.htm",
                "provider": "sec",
            }
        )
    ],
    openapi_extra={
        "widget_config": {
            "description": "Get a list of all the documents associated with a filing, and their direct URLs.",
            "gridData": {
                "w": 30,
                "h": 10,
            },
            "refetchInterval": False,
            "data": {"dataKey": "results.document_urls"},
        }
    },
)
async def filing_headers(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Download the index headers, and cover page if available, for any SEC filing."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="SecFullTextSearch",
    examples=[
        APIEx(parameters={"query": "climate change", "provider": "sec"}),
        APIEx(parameters={"entity": "AAPL", "form_type": "10-K", "provider": "sec"}),
    ],
    openapi_extra={
        "widget_config": {
            "name": "Full-Text Search",
            "description": "Search the full text of all EDGAR filings since 2001."
            " Click a row's Document cell to load that filing in the Index Headers"
            " and Filing Viewer widgets.",
            "type": "table",
            "runButton": True,
            "refetchInterval": False,
            "gridData": {"w": 20, "h": 14},
            "data": {
                "dataKey": "results",
                "table": {
                    "showAll": True,
                    "enableAdvanced": True,
                    "columnsDefs": [
                        {
                            "field": "url",
                            "headerName": "Document",
                            "headerTooltip": "Click to load this filing in the Index"
                            " Headers and Filing Viewer widgets.",
                            "pinned": "left",
                            "cellDataType": "text",
                            "renderFn": "cellOnClick",
                            "renderFnParams": {
                                "actionType": "groupBy",
                                "groupBy": {"paramName": "url"},
                            },
                        },
                        {
                            "field": "filing_date",
                            "headerName": "Filing Date",
                            "cellDataType": "date",
                        },
                        {
                            "field": "form",
                            "headerName": "Form",
                            "cellDataType": "text",
                        },
                        {
                            "field": "name",
                            "headerName": "Company",
                            "cellDataType": "text",
                        },
                        {
                            "field": "symbol",
                            "headerName": "Symbol",
                            "cellDataType": "text",
                        },
                        {
                            "field": "cik",
                            "headerName": "CIK",
                            "cellDataType": "text",
                        },
                        {
                            "field": "description",
                            "headerName": "Description",
                            "cellDataType": "text",
                        },
                    ],
                },
            },
        }
    },
)
async def full_text_search(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Search the full text of all SEC EDGAR filings since 2001."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="SecHtmFile",
    examples=[
        APIEx(
            parameters={
                "url": "https://www.sec.gov/Archives/edgar/data/1723690/000119312525030074/d866336dex991.htm",
                "provider": "sec",
            }
        )
    ],
    openapi_extra={
        "widget_config": {
            "name": "Open HTML",
            "description": "Open a HTM/HTML document from the SEC website.",
            "gridData": {
                "w": 40,
                "h": 25,
            },
            "refetchInterval": False,
            "type": "markdown",
            "data": {
                "dataKey": "results.content",
            },
        }
    },
)
async def htm_file(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Download a raw HTML object from the SEC website."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="CikMap",
    examples=[APIEx(parameters={"symbol": "MSFT", "provider": "sec"})],
)
async def cik_map(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Map a ticker symbol to a CIK number."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="InstitutionsSearch",
    examples=[
        APIEx(parameters={"provider": "sec"}),
        APIEx(parameters={"query": "blackstone real estate", "provider": "sec"}),
    ],
)
async def institutions_search(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Search SEC-regulated institutions by name and return a list of results with CIK numbers."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="SecAdviserFirms",
    examples=[
        APIEx(parameters={"query": "blackrock", "provider": "sec"}),
    ],
)
async def adviser_firms(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Search SEC investment adviser firms."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="SecAdviserIndividuals",
    examples=[
        APIEx(parameters={"query": "john smith", "provider": "sec"}),
    ],
)
async def adviser_individuals(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Search SEC adviser individuals, with one row per current employer."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="SecAdviserDocuments",
    examples=[
        APIEx(parameters={"crd": "148826", "provider": "sec"}),
    ],
)
async def adviser_documents(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """List available Form ADV and brochure documents by firm CRD."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="SecAdviserUniverse",
    examples=[
        APIEx(parameters={"registration_type": "registered", "provider": "sec"}),
        APIEx(parameters={"registration_type": "exempt", "provider": "sec"}),
        APIEx(
            parameters={
                "registration_type": "registered",
                "crd": "148826",
                "provider": "sec",
            }
        ),
    ],
)
async def adviser_universe(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get current registered or exempt Form ADV Part 1 data, optionally by CRD."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="SchemaFiles",
    examples=[
        APIEx(parameters={"provider": "sec"}),
        PythonEx(
            description="Explore XBRL taxonomies progressively.",
            code=[
                "# List all available taxonomy families",
                "obb.sec.schema_files(provider='sec')",
                "# List components for US GAAP (latest year)",
                "obb.sec.schema_files(taxonomy='us-gaap', provider='sec')",
                "# List presentation components for US GAAP 2024",
                "obb.sec.schema_files(taxonomy='us-gaap', year=2024, provider='sec')",
                "# Get the Statement of Income presentation structure",
                "obb.sec.schema_files(taxonomy='us-gaap', year=2024, component='soi', provider='sec')",
            ],
        ),
    ],
)
async def schema_files(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Explore SEC and FASB XBRL taxonomy schemas, labels, and presentation structures.

    - No parameters: list all available taxonomy families.
    - taxonomy only: get all parsed structures for the most recent year.
    - taxonomy + year: get all parsed structures for a specific year.
    - taxonomy + component: get one component's structure using the most recent year.
    - taxonomy + year + component: get one component's parsed structure.
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="SymbolMap",
    examples=[APIEx(parameters={"query": "0000789019", "provider": "sec"})],
)
async def symbol_map(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Map a CIK number to a ticker symbol, leading 0s can be omitted or included."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="RssLitigation",
    examples=[APIEx(parameters={"provider": "sec"})],
)
async def rss_litigation(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the RSS feed that provides links to litigation releases concerning civil lawsuits brought by the Commission in federal court."""  # noqa: E501
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="SicSearch",
    examples=[
        APIEx(parameters={"provider": "sec"}),
        APIEx(parameters={"query": "real estate investment trusts", "provider": "sec"}),
    ],
)
async def sic_search(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Search for Industry Titles, Reporting Office, and SIC Codes. An empty query string returns all results."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="SecAsFiledStatements",
    examples=[
        APIEx(parameters={"symbol": "AAPL", "provider": "sec"}),
        APIEx(
            parameters={
                "symbol": "AAPL",
                "statement_type": "balance",
                "provider": "sec",
            }
        ),
    ],
)
async def financial_statements(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the financial statements exactly as reported in a company's latest 10-K/10-Q filing."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="SecCompanyOverview",
    examples=[APIEx(parameters={"symbol": "AAPL", "provider": "sec"})],
)
async def company_overview(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the company overview - entity profile and Business (Item 1) section - from a filing."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="SecExecutiveCompensation",
    examples=[APIEx(parameters={"symbol": "AAPL", "provider": "sec"})],
)
async def executive_compensation(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Summary Compensation Table from a company's proxy statement (DEF 14A)."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="SecBeneficialOwnership",
    examples=[APIEx(parameters={"symbol": "AAPL", "provider": "sec"})],
)
async def beneficial_ownership(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the 5%+ beneficial owners table from a company's proxy statement (DEF 14A)."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="SecManagementProfiles",
    examples=[APIEx(parameters={"symbol": "AAPL", "provider": "sec"})],
)
async def management_profiles(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get management profiles from annual filings and referenced proxy statements."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="SecPayVersusPerformance",
    examples=[APIEx(parameters={"symbol": "AAPL", "provider": "sec"})],
)
async def pay_versus_performance(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Pay Versus Performance disclosure (Item 402(v)) XBRL facts from a proxy."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="SecDisclosures",
    examples=[APIEx(parameters={"symbol": "AAPL", "provider": "sec"})],
)
async def disclosures(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the disclosure text blocks and tables - notes to the financial statements - from a filing."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="SecRiskFactors",
    examples=[APIEx(parameters={"symbol": "AAPL", "provider": "sec"})],
)
async def risk_factors(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Risk Factors (Item 1A) section from a company's latest 10-K/10-Q filing."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="SecSegmentRevenue",
    examples=[APIEx(parameters={"symbol": "AAPL", "provider": "sec"})],
)
async def segment_revenue(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the segment and geographic breakdown of revenues from a filing's XBRL data."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="SecLegalProceedings",
    examples=[APIEx(parameters={"symbol": "AAPL", "provider": "sec"})],
)
async def legal_proceedings(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Legal Proceedings section (Item 3 / Part II Item 1) from a filing."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="SecExhibit",
    examples=[APIEx(parameters={"symbol": "AAPL", "provider": "sec"})],
)
async def exhibit(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get a single attached exhibit document from a filing, rendered as markdown."""
    return await OBBject.from_query(Query(**locals()))


from openbb_sec import EQUITY_INSTALLED, ETF_INSTALLED  # noqa: E402

if not EQUITY_INSTALLED:

    @router.command(
        model="SecBalanceSheet",
        examples=[
            APIEx(parameters={"symbol": "AAPL", "provider": "sec"}),
            APIEx(
                parameters={
                    "symbol": "AAPL",
                    "period": "annual",
                    "limit": 5,
                    "provider": "sec",
                }
            ),
        ],
    )
    async def balance_sheet(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Get the balance sheet for a given company."""
        return await OBBject.from_query(Query(**locals()))

    @router.command(
        model="SecBalanceSheetGrowth",
        examples=[
            APIEx(parameters={"symbol": "AAPL", "provider": "sec"}),
            APIEx(parameters={"symbol": "AAPL", "limit": 10, "provider": "sec"}),
        ],
    )
    async def balance_sheet_growth(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Get the growth of a company's balance sheet items over time."""
        return await OBBject.from_query(Query(**locals()))

    @router.command(
        model="SecCashFlowStatement",
        examples=[
            APIEx(parameters={"symbol": "AAPL", "provider": "sec"}),
            APIEx(
                parameters={
                    "symbol": "AAPL",
                    "period": "annual",
                    "limit": 5,
                    "provider": "sec",
                }
            ),
        ],
    )
    async def cash_flow(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Get the cash flow statement for a given company."""
        return await OBBject.from_query(Query(**locals()))

    @router.command(
        model="SecCashFlowStatementGrowth",
        examples=[
            APIEx(parameters={"symbol": "AAPL", "provider": "sec"}),
            APIEx(parameters={"symbol": "AAPL", "limit": 10, "provider": "sec"}),
        ],
    )
    async def cash_flow_growth(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Get the growth of a company's cash flow statement items over time."""
        return await OBBject.from_query(Query(**locals()))

    @router.command(
        model="SecIncomeStatement",
        examples=[
            APIEx(parameters={"symbol": "AAPL", "provider": "sec"}),
            APIEx(
                parameters={
                    "symbol": "AAPL",
                    "period": "annual",
                    "limit": 5,
                    "provider": "sec",
                }
            ),
        ],
    )
    async def income_statement(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Get the income statement for a given company."""
        return await OBBject.from_query(Query(**locals()))

    @router.command(
        model="SecIncomeStatementGrowth",
        examples=[
            APIEx(parameters={"symbol": "AAPL", "provider": "sec"}),
            APIEx(
                parameters={
                    "symbol": "AAPL",
                    "limit": 10,
                    "period": "annual",
                    "provider": "sec",
                }
            ),
        ],
    )
    async def income_statement_growth(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Get the growth of a company's income statement items over time."""
        return await OBBject.from_query(Query(**locals()))

    @router.command(
        model="SecCompanyFilings",
        examples=[
            APIEx(parameters={"symbol": "AAPL", "provider": "sec"}),
            APIEx(parameters={"limit": 100, "provider": "sec"}),
        ],
    )
    async def company_filings(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Get public company filings."""
        return await OBBject.from_query(Query(**locals()))

    @router.command(
        model="SecCompareCompanyFacts",
        examples=[
            APIEx(parameters={"provider": "sec"}),
            APIEx(
                parameters={
                    "provider": "sec",
                    "fact": "PaymentsForRepurchaseOfCommonStock",
                    "year": 2023,
                }
            ),
            APIEx(
                parameters={
                    "provider": "sec",
                    "symbol": "NVDA,AAPL,AMZN,MSFT,GOOG,SMCI",
                    "fact": "RevenueFromContractWithCustomerExcludingAssessedTax",
                    "year": 2024,
                }
            ),
        ],
    )
    async def compare_company_facts(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Compare reported company facts and fundamental data points."""
        return await OBBject.from_query(Query(**locals()))

    @router.command(
        model="SecEquitySearch",
        examples=[
            APIEx(parameters={"provider": "sec"}),
            APIEx(parameters={"query": "AAPL", "provider": "sec"}),
        ],
    )
    async def equity_search(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Search for stock symbol, CIK, LEI, or company name."""
        return await OBBject.from_query(Query(**locals()))

    @router.command(
        model="SecLatestFinancialReports",
        examples=[
            APIEx(parameters={"provider": "sec"}),
            APIEx(parameters={"provider": "sec", "date": "2024-09-30"}),
        ],
    )
    async def latest_financial_reports(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Get the newest quarterly, annual, and current reports for all companies."""
        return await OBBject.from_query(Query(**locals()))

    @router.command(
        model="SecInsiderTrading",
        examples=[
            APIEx(parameters={"symbol": "AAPL", "provider": "sec"}),
        ],
    )
    async def insider_trading(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Get data about trading by a company's management team and board of directors."""
        return await OBBject.from_query(Query(**locals()))

    @router.command(
        model="SecForm13FHR",
        examples=[
            APIEx(parameters={"symbol": "NVDA", "provider": "sec"}),
            APIEx(
                description="Enter a date (calendar quarter ending) for a specific report.",
                parameters={"symbol": "BRK-A", "date": "2016-09-30", "provider": "sec"},
            ),
        ],
    )
    async def form_13f(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Get the form 13F.

        The Securities and Exchange Commission's (SEC) Form 13F is a quarterly
        report that is required to be filed by all institutional investment
        managers with at least $100 million in assets under management.
        Managers are required to file Form 13F within 45 days after the last
        day of the calendar quarter. Most funds wait until the end of this
        period in order to conceal their investment strategy from competitors
        and the public.
        """
        return await OBBject.from_query(Query(**locals()))

    @router.command(
        model="SecEquityFtd",
        examples=[APIEx(parameters={"symbol": "AAPL", "provider": "sec"})],
    )
    async def equity_ftd(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Get reported Fail-to-deliver (FTD) data."""
        return await OBBject.from_query(Query(**locals()))

    @router.command(
        model="SecManagementDiscussionAnalysis",
        examples=[
            APIEx(parameters={"symbol": "AAPL", "provider": "sec"}),
            APIEx(
                description="Get the Management Discussion & Analysis section by calendar year and period.",
                parameters={
                    "symbol": "AAPL",
                    "calendar_year": 2020,
                    "calendar_period": "Q4",
                    "provider": "sec",
                },
            ),
            APIEx(
                description="Setting 'include_tables' to True will attempt to extract all tables in valid Markdown.",
                parameters={
                    "symbol": "AAPL",
                    "calendar_year": 2020,
                    "calendar_period": "Q4",
                    "provider": "sec",
                    "include_tables": True,
                },
            ),
            APIEx(
                description="Setting 'raw_html' to True will bypass extraction and return the raw HTML file, as is."
                + " Use this for custom parsing or to access the entire HTML filing.",
                parameters={
                    "symbol": "AAPL",
                    "calendar_year": 2020,
                    "calendar_period": "Q4",
                    "provider": "sec",
                    "raw_html": True,
                },
            ),
        ],
        openapi_extra={
            "widget_config": {
                "type": "markdown",
                "data": {"dataKey": "results.content", "columnsDefs": []},
                "staleTime": 86400000,
                "refetchInterval": 86400000,
                "source": "SEC",
            }
        },
    )
    async def management_discussion_analysis(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Get the Management Discussion & Analysis section from the financial statements for a given company."""
        return await OBBject.from_query(Query(**locals()))

else:
    _FILINGS_TABLE = {
        "name": "Company Filings",
        "description": "Browse a company's SEC filings. Click a row's Document cell to"
        " load that filing in the Index Headers and Filing Viewer widgets.",
        "type": "table",
        "refetchInterval": False,
        "gridData": {"w": 20, "h": 14},
        "data": {
            "dataKey": "results",
            "table": {
                "showAll": True,
                "enableAdvanced": True,
                "columnsDefs": [
                    {
                        "field": "report_url",
                        "headerName": "Document",
                        "pinned": "left",
                        "cellDataType": "text",
                        "renderFn": "cellOnClick",
                        "renderFnParams": {
                            "actionType": "groupBy",
                            "groupBy": {
                                "paramName": "url",
                                "valueField": "report_url",
                            },
                        },
                    },
                    {
                        "field": "filing_date",
                        "headerName": "Filing Date",
                        "cellDataType": "date",
                    },
                    {
                        "field": "report_type",
                        "headerName": "Form",
                        "cellDataType": "text",
                    },
                    {
                        "field": "report_date",
                        "headerName": "Report Date",
                        "cellDataType": "date",
                    },
                    {
                        "field": "accession_number",
                        "headerName": "Accession",
                        "cellDataType": "text",
                    },
                    {
                        "field": "filing_detail_url",
                        "headerName": "Index Page",
                        "cellDataType": "text",
                    },
                ],
            },
        },
    }
    _LATEST_TABLE = {
        "name": "Latest Financial Reports",
        "description": "The newest annual, quarterly, and current reports filed by all"
        " companies. Click a row's Document cell to load that filing in the Index"
        " Headers and Filing Viewer widgets.",
        "type": "table",
        "refetchInterval": False,
        "gridData": {"w": 20, "h": 14},
        "data": {
            "dataKey": "results",
            "table": {
                "showAll": True,
                "enableAdvanced": True,
                "columnsDefs": [
                    {
                        "field": "url",
                        "headerName": "Document",
                        "pinned": "left",
                        "cellDataType": "text",
                        "renderFn": "cellOnClick",
                        "renderFnParams": {
                            "actionType": "groupBy",
                            "groupBy": {"paramName": "url"},
                        },
                    },
                    {
                        "field": "filing_date",
                        "headerName": "Filing Date",
                        "cellDataType": "date",
                    },
                    {
                        "field": "report_type",
                        "headerName": "Form",
                        "cellDataType": "text",
                    },
                    {"field": "name", "headerName": "Company", "cellDataType": "text"},
                    {"field": "symbol", "headerName": "Symbol", "cellDataType": "text"},
                    {
                        "field": "period_ending",
                        "headerName": "Period",
                        "cellDataType": "date",
                    },
                    {
                        "field": "description",
                        "headerName": "Description",
                        "cellDataType": "text",
                    },
                ],
            },
        },
    }

    @router.command(
        model="Filings",
        examples=[APIEx(parameters={"symbol": "AAPL", "provider": "sec"})],
        openapi_extra={"widget_config": _FILINGS_TABLE},
    )
    async def company_filings(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Get public company filings."""
        return await OBBject.from_query(Query(**locals()))

    @router.command(
        model="LatestFinancialReports",
        examples=[APIEx(parameters={"provider": "sec"})],
        openapi_extra={"widget_config": _LATEST_TABLE},
    )
    async def latest_financial_reports(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Get the newest quarterly, annual, and current reports for all companies."""
        return await OBBject.from_query(Query(**locals()))


if not ETF_INSTALLED:

    @router.command(
        model="SecNportDisclosure",
        examples=[
            APIEx(
                parameters={
                    "symbol": "XLK",
                    "provider": "sec",
                    "year": 2025,
                    "quarter": 1,
                }
            ),
        ],
    )
    async def nport_disclosure(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Get SEC NPORT-P disclosure filings for a given ETF or mutual fund (US only)."""
        return await OBBject.from_query(Query(**locals()))


@router.command(
    model="SecNportFundMetrics",
    examples=[APIEx(parameters={"symbol": "XLK", "provider": "sec"})],
    openapi_extra={
        "widget_config": {
            "name": "Fund Performance & Flows",
            "description": "Monthly total return, net assets, and creation/redemption"
            " flows from the fund's most recent NPORT-P filing.",
            "refetchInterval": False,
            "gridData": {"w": 40, "h": 8},
        }
    },
)
async def nport_fund_metrics(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get fund performance, net assets, and flows from the latest NPORT-P filing."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    methods=["GET"],
    include_in_schema=False,
    openapi_extra={"widget_config": {"exclude": True}},
    examples=[APIEx(parameters={"provider": "sec", "symbol": "AAPL"})],
)
async def filing_options(
    symbol: Annotated[
        str | None,
        FastAPIQuery(description="Symbol to list available filing years for."),
    ] = None,
) -> list:
    """Options endpoint for the filing 'year' dependent dropdown.

    Returns a list of {'value', 'label'} for the years a symbol has 10-K/10-Q filings.
    """
    from openbb_sec.models.sec_financials import get_form10_urls_by_symbol

    if not symbol:
        return []

    filings = await get_form10_urls_by_symbol(symbol.upper(), True)
    years = sorted(
        {str(f["period_ending"])[:4] for f in filings if f.get("period_ending")},
        reverse=True,
    )
    return [{"value": year, "label": year} for year in years]


@router.api_router.get("/exhibits", include_in_schema=False)
async def exhibits(
    symbol: Annotated[str | None, FastAPIQuery(description="Ticker symbol.")] = None,
    calendar_year: Annotated[
        str | None, FastAPIQuery(description="Calendar year of the filing.")
    ] = None,
    calendar_period: Annotated[
        str | None,
        FastAPIQuery(description="Calendar quarter (Q1-Q4); empty for the latest."),
    ] = None,
    use_cache: Annotated[bool, FastAPIQuery(description="Use the cache.")] = True,
) -> list:
    """Options endpoint for the exhibit-dependent dropdown.

    Returns {'value', 'label'} for each exhibit attached to the resolved filing.
    """
    from openbb_sec.models.sec_financials import (
        FinancialStatements,
        resolve_filing_url,
    )

    if not symbol:
        return []
    url = await resolve_filing_url(
        symbol.upper(),
        int(calendar_year) if calendar_year else None,
        calendar_period or None,
        use_cache,
        annual_default=False,
    )
    if not url:
        return []
    return FinancialStatements.from_url(url, use_cache).exhibit_choices()


@router.api_router.get("/companies", include_in_schema=False)
async def companies(
    use_cache: Annotated[
        bool, FastAPIQuery(description="Use the cached company list.")
    ] = True,
) -> list:
    """Options endpoint: companies with standardized SEC financials (DoltHub-sourced)."""
    from openbb_sec.utils.company_choices import get_company_choices

    return await get_company_choices(use_cache=use_cache)


@router.api_router.get("/nport_funds", include_in_schema=False)
async def nport_funds(
    use_cache: Annotated[
        bool, FastAPIQuery(description="Use the cached fund list.")
    ] = True,
) -> list:
    """Options endpoint: mutual funds and ETFs mapped to their SEC series codes."""
    from openbb_sec.utils.helpers import get_nport_fund_choices

    return await get_nport_fund_choices(use_cache=use_cache)


@router.api_router.get("/13f_filers", include_in_schema=False)
async def filers_13f(
    use_cache: Annotated[
        bool, FastAPIQuery(description="Use the cached filer list.")
    ] = True,
) -> list:
    """Options endpoint: current 13F filers (institutions and companies) by name."""
    from openbb_sec.utils.helpers import get_13f_filer_choices

    return await get_13f_filer_choices(use_cache=use_cache)


@router.api_router.get("/13f_periods", include_in_schema=False)
async def periods_13f(
    symbol: Annotated[
        str | None, FastAPIQuery(description="13F filer symbol or CIK.")
    ] = None,
) -> list:
    """Options endpoint: report periods (calendar quarter ends) a filer has on file."""
    from openbb_sec.utils import parse_13f

    if not symbol:
        return []
    try:
        filings = (
            await parse_13f.get_13f_candidates(cik=symbol)
            if symbol.isnumeric()
            else await parse_13f.get_13f_candidates(symbol=symbol)
        )
    except Exception:  # noqa: BLE001
        return []
    dates = sorted({str(period)[:10] for period in filings.index}, reverse=True)
    return [{"label": period, "value": period} for period in dates]


@router.api_router.get("/nport_periods", include_in_schema=False)
async def nport_periods(
    symbol: Annotated[
        str | None, FastAPIQuery(description="Fund ticker symbol.")
    ] = None,
    use_cache: Annotated[bool, FastAPIQuery(description="Use the cache.")] = True,
) -> list:
    """Options endpoint: actual filing periods (NPORT-P/N-MFP) available for a fund."""
    from openbb_sec.utils.helpers import get_nport_candidates

    if not symbol:
        return []
    try:
        filings = await get_nport_candidates(symbol.upper(), use_cache)
    except Exception:  # noqa: BLE001
        return []
    seen: set = set()
    choices: list = []
    for filing in filings:
        period = str(filing.get("period_ending") or "")[:10]
        if period and period not in seen:
            seen.add(period)
            choices.append(
                {"label": f"{period} ({filing.get('form_type')})", "value": period}
            )
    return choices


@router.api_router.get("/form_types", include_in_schema=False)
async def form_types(
    symbol: Annotated[str | None, FastAPIQuery(description="Ticker symbol.")] = None,
    use_cache: Annotated[bool, FastAPIQuery(description="Use the cache.")] = True,
) -> list:
    """Options endpoint: form types actually present in the company's filings."""
    from openbb_core.provider.abstract.annotated_result import AnnotatedResult

    from openbb_sec.models.company_filings import SecCompanyFilingsFetcher

    if not symbol:
        return []
    try:
        fetched = await SecCompanyFilingsFetcher().fetch_data(
            {"symbol": symbol.upper(), "use_cache": use_cache, "limit": 0}, {}
        )
    except Exception:  # noqa: BLE001
        return []
    rows = (fetched.result or []) if isinstance(fetched, AnnotatedResult) else fetched
    forms = sorted({r.report_type for r in rows if r.report_type})
    return [{"label": form, "value": form} for form in forms]


@router.api_router.get("/report_types", include_in_schema=False)
async def report_types() -> list:
    """Options endpoint: form types for the Latest Reports filter."""
    from openbb_sec.models.latest_financial_reports import report_type_choices

    return [{"label": form, "value": form} for form in report_type_choices]


@router.api_router.get("/section_markdown", include_in_schema=False)
async def section_markdown(
    symbol: Annotated[str | None, FastAPIQuery(description="Ticker symbol.")] = None,
    section: Annotated[
        str,
        FastAPIQuery(
            description="company_overview, risk_factors, segment_revenue,"
            " legal_proceedings, or disclosures."
        ),
    ] = "risk_factors",
    calendar_year: Annotated[
        str | None, FastAPIQuery(description="Calendar year of the filing.")
    ] = None,
    calendar_period: Annotated[
        str | None,
        FastAPIQuery(
            description="Calendar quarter (Q1-Q4); empty for the latest annual."
        ),
    ] = None,
    use_cache: Annotated[bool, FastAPIQuery(description="Use the cache.")] = True,
) -> str:
    """Render a filing section as a single markdown string for a Workspace widget."""
    from openbb_sec.utils.section_markdown import get_section_markdown

    if not symbol:
        return ""
    return await get_section_markdown(
        symbol.upper(),
        section,
        calendar_year or None,
        calendar_period or None,
        use_cache,
    )


@router.api_router.get("/edgar_document", include_in_schema=False)
async def edgar_document(  # noqa: PLR0911, PLR0912
    url: Annotated[
        str | None,
        FastAPIQuery(description="Direct URL of a SEC EDGAR filing document."),
    ] = None,
    use_cache: Annotated[bool, FastAPIQuery(description="Use the cache.")] = True,
):
    """Serve a SEC filing document for the viewer iframe, same-origin."""
    import asyncio
    import contextlib
    import re as _re

    from fastapi.responses import HTMLResponse, Response

    from openbb_sec.utils.cache import cached_bytes
    from openbb_sec.utils.definitions import SEC_HEADERS

    if not url:
        return HTMLResponse("<p style='font-family:sans-serif'>Select a filing.</p>")
    if not url.startswith(("https://www.sec.gov/", "https://efts.sec.gov/")):
        return HTMLResponse(
            "<p style='font-family:sans-serif'>Only SEC EDGAR URLs are supported.</p>",
            status_code=400,
        )

    async def _get(target: str) -> bytes:
        return await asyncio.to_thread(
            cached_bytes, target, use_cache=use_cache, headers=SEC_HEADERS
        )

    def _bounded_get(target: str, limit: int) -> bytes:
        """Stream at most ``limit`` bytes so huge files never load in full."""
        from openbb_sec.utils.ratelimit import sec_make_request

        headers = {**SEC_HEADERS, "Accept-Encoding": "identity"}
        resp = sec_make_request(target, headers=headers, stream=True, timeout=30)
        try:
            if getattr(resp, "status_code", 200) >= 400:
                return b""
            out = bytearray()
            for piece in resp.iter_content(65536):
                if piece:
                    out += piece
                if len(out) >= limit:
                    break
            return bytes(out[:limit])
        finally:
            with contextlib.suppress(Exception):
                resp.close()

    def _rewrite_urls(content: str, doc_url: str) -> str:
        from urllib.parse import quote

        directory = doc_url.rsplit("/", 1)[0] + "/"

        def _abs(value: str) -> str:
            v = value.strip()
            if v.startswith(("http://", "https://")):
                return v
            if v.startswith("//"):
                return "https:" + v
            if v.startswith("/"):
                return "https://www.sec.gov" + v
            return directory + v

        def _proxy(value: str) -> str:
            # Relative path: resolves against the viewer's base URL, so it works
            # under any API prefix (/api/v1, /api/v2, ...) without hard-coding it.
            return "edgar_document?url=" + quote(_abs(value), safe="")

        def _inline(value: str) -> bool:
            v = value.strip()
            for q in ("&#39;", "&#34;", "&quot;", "'", '"'):
                if v.startswith(q):
                    v = v[len(q) :]
                    break
            return v.startswith(("data:", "#"))

        def _src(match):
            attr, quote_ch, value = match.group(1), match.group(2), match.group(3)
            if _inline(value):
                return match.group(0)
            return f"{attr}={quote_ch}{_proxy(value)}{quote_ch}"

        def _css(match):
            quote_ch, value = match.group(1), match.group(2)
            if _inline(value):
                return match.group(0)
            return f"url({quote_ch}{_proxy(value)}{quote_ch})"

        def _href(match):
            quote_ch, value = match.group(1), match.group(2)
            if value.strip().startswith(
                ("#", "http://", "https://", "//", "data:", "mailto:", "javascript:")
            ):
                return match.group(0)
            return f"href={quote_ch}{_abs(value)}{quote_ch}"

        content = _re.sub(
            r'(src|poster)\s*=\s*(["\'])([^"\']*)\2',
            _src,
            content,
            flags=_re.IGNORECASE,
        )
        content = _re.sub(
            r'url\(\s*(["\']?)([^"\')]+)\1\s*\)', _css, content, flags=_re.IGNORECASE
        )
        return _re.sub(
            r'href\s*=\s*(["\'])([^"\']*)\1', _href, content, flags=_re.IGNORECASE
        )

    async def _rendered_html(target: str) -> str | None:
        directory, filename = target.rsplit("/", 1)
        accession = directory.rsplit("/", 1)[-1]
        if not (len(accession) == 18 and accession.isdigit()):
            return None
        dashed = f"{accession[:10]}-{accession[10:12]}-{accession[12:]}"
        try:
            index_html = (await _get(f"{directory}/{dashed}-index.html") or b"").decode(
                "utf-8", errors="ignore"
            )
            link = _re.search(
                r'href="([^"]*/xsl[^"/]*/' + _re.escape(filename) + r')"',
                index_html,
                _re.IGNORECASE,
            )
            if not link:
                return None
            rendered_url = link.group(1)
            if not rendered_url.startswith("http"):
                rendered_url = "https://www.sec.gov" + rendered_url
            rendered = (await _get(rendered_url) or b"").decode(
                "utf-8", errors="ignore"
            )
            return _rewrite_urls(rendered, rendered_url) if rendered else None
        except Exception:  # noqa: BLE001
            return None

    path = url.split("?", 1)[0].lower()

    if path.endswith(".xml") and "/xsl" not in path:
        rendered = await _rendered_html(url)
        if rendered is not None:
            return Response(content=rendered, media_type="text/html")
        from openbb_sec.utils.xml_render import render_xml_as_html

        limit = 5_000_000
        chunk = await asyncio.to_thread(_bounded_get, url, limit)
        if chunk:
            structured = render_xml_as_html(
                chunk, source_url=url, truncated=len(chunk) >= limit
            )
            if structured is not None:
                return Response(content=structured, media_type="text/html")
            from openbb_sec.utils.xbrl_render import _looks_xbrl, render_xbrl_facts

            if _looks_xbrl(chunk):
                from openbb_sec.utils.financial_report import render_financial_report

                report = await render_financial_report(
                    url.rsplit("/", 1)[0] + "/", use_cache
                )
                if report is not None:
                    return Response(content=report, media_type="text/html")
            xbrl = render_xbrl_facts(
                chunk, source_url=url, truncated=len(chunk) >= limit
            )
            if xbrl is not None:
                return Response(content=xbrl, media_type="text/html")
            return Response(
                content=chunk.decode("utf-8", errors="ignore"),
                media_type="text/plain; charset=utf-8",
            )

    try:
        raw = await _get(url)
    except Exception:  # noqa: BLE001
        return HTMLResponse(
            "<p style='font-family:sans-serif'>Could not load the document.</p>",
            status_code=502,
        )
    raw = raw or b""
    image_exts = (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tif", ".tiff")
    binary_type = None
    if path.endswith(".pdf") or raw[:5] == b"%PDF-":
        binary_type = "application/pdf"
    elif (
        path.endswith(image_exts)
        or raw[:3] == b"\xff\xd8\xff"
        or raw[:8] == b"\x89PNG\r\n\x1a\n"
        or raw[:6] in (b"GIF87a", b"GIF89a")
    ):
        import mimetypes

        binary_type = mimetypes.guess_type(path)[0] or "application/octet-stream"
    if binary_type:
        return Response(content=raw, media_type=binary_type)

    text = raw.decode("utf-8", errors="ignore")

    looks_html = path.endswith((".htm", ".html")) or bool(
        _re.search(r"(?i)<html|<body|<!doctype", text[:2000])
    )
    html = _rewrite_urls(text, url) if looks_html else None

    if html is None and "/xsl" not in path:
        html = await _rendered_html(url)

    if html is not None:
        return Response(content=html, media_type="text/html")
    return Response(content=text, media_type="text/plain; charset=utf-8")


@router.api_router.get("/filing_viewer_app", include_in_schema=False)
async def filing_viewer_app():
    """Serve the Filing Viewer iframe app."""
    from pathlib import Path

    from fastapi.responses import HTMLResponse

    app_html = (Path(__file__).parent / "assets" / "filing_viewer_app.html").read_text(
        encoding="utf-8"
    )
    return HTMLResponse(content=app_html)


class SecAssetDataRowsRequest(AgGridRowsRequest):
    """SSRM request body for asset-data rows, carrying the document URL."""

    document_url: str = ""


class AssetDataRowsResponse(BaseModel):
    """A page of asset-data rows for an AgGrid datasource."""

    rowData: list[dict]
    rowCount: int
    columns: list[str]


@router.api_router.post("/asset_data_rows", include_in_schema=False)
async def asset_data_rows(body: SecAssetDataRowsRequest) -> AssetDataRowsResponse:
    """Serve a paged/sorted/filtered block of asset-data rows for the viewer grid."""
    import asyncio

    from openbb_sec.utils.asset_data import load_asset_data, query

    url = body.document_url
    empty = AssetDataRowsResponse(rowData=[], rowCount=0, columns=[])
    if not url or not url.startswith(("https://www.sec.gov/", "https://efts.sec.gov/")):
        return empty
    try:
        columns, rows = await asyncio.to_thread(load_asset_data, url)
    except Exception:  # noqa: BLE001
        return empty
    if not columns:
        return empty
    row_data, total = query(columns, rows, body)
    return AssetDataRowsResponse(rowData=row_data, rowCount=total, columns=columns)


@router.api_router.get("/edgar_document_markdown", include_in_schema=False)
async def edgar_document_markdown(
    url: Annotated[
        str | None, FastAPIQuery(description="Direct URL of a SEC EDGAR document.")
    ] = None,
) -> dict:
    """Serve a SEC filing document as text/markdown for the viewer's sub-widget."""
    import asyncio

    from openbb_sec.utils.filing_viewer_mcp import document_to_markdown

    if not url:
        return {"content": ""}
    content = await asyncio.to_thread(document_to_markdown, url)
    return {"content": content}


@router.api_router.get("/fts_categories", include_in_schema=False)
async def fts_categories() -> list:
    """Options endpoint: EDGAR filing categories for the full-text search filter."""
    from openbb_sec.utils.fts_lookups import FTS_CATEGORIES

    return FTS_CATEGORIES


@router.api_router.get("/fts_form_types", include_in_schema=False)
async def fts_form_types() -> list:
    """Options endpoint: individual form types for the full-text search filter."""
    from openbb_sec.utils.definitions import FORM_LIST

    forms = sorted({form.replace("_", " ") for form in FORM_LIST})
    return [{"label": form, "value": form} for form in forms]


@router.api_router.get("/fts_locations", include_in_schema=False)
async def fts_locations() -> list:
    """Options endpoint: principal-executive-office locations for full-text search."""
    from openbb_sec.utils.fts_lookups import FTS_LOCATIONS

    return FTS_LOCATIONS


_PRIME_TASKS: set = set()


def _mcp_public_url() -> str:
    """Absolute URL the Workspace connects to for the Filing Viewer MCP.

    The server runs as a subprocess reverse-proxied through the OpenBB API (see
    the route below), so it lives on the API's own host/port. It must be absolute
    — a relative path resolves against the Workspace origin, not the backend, so
    the connection never reaches here. Built from the API port; override the whole
    URL with ``OPENBB_SEC_MCP_PUBLIC_URL`` (or just the host with
    ``OPENBB_SEC_MCP_PUBLIC_HOST``) for non-local deployments.
    """
    import os
    import sys

    from openbb_core.app.service.system_service import SystemService

    override = os.environ.get("OPENBB_SEC_MCP_PUBLIC_URL")
    if override:
        return override

    # openbb-api/uvicorn take --port on the command line and do not export it, so
    # read it from argv (then env, then the default).
    port = None
    for i, arg in enumerate(sys.argv):
        if arg == "--port" and i + 1 < len(sys.argv):
            port = sys.argv[i + 1]
        elif arg.startswith("--port="):
            port = arg.split("=", 1)[1]
    port = os.environ.get("OPENBB_API_PORT") or port or "6900"

    prefix = SystemService().system_settings.api_settings.prefix
    host = os.environ.get("OPENBB_SEC_MCP_PUBLIC_HOST", "127.0.0.1")
    return f"http://{host}:{port}{prefix}/sec/filing_viewer_mcp/mcp"


from openbb_sec.utils.filing_viewer_mcp import (  # noqa: E402
    ensure_mcp_subprocess,
    mcp_reverse_proxy,
)

# Expose the Filing Viewer MCP server on the OpenBB API's own host/port by
# reverse-proxying to the local subprocess that serves streamable-http. The
# {path:path} catch-all forwards both /mcp (the transport) and /viewer-state
# (the iframe's current-document ping).
router.api_router.add_api_route(
    path="/filing_viewer_mcp/{path:path}",
    endpoint=mcp_reverse_proxy,
    methods=["GET", "POST", "DELETE"],
    include_in_schema=False,
)


async def _warm_companies() -> None:
    """Best-effort warm of the DoltHub company-choices cache."""
    import contextlib

    from openbb_sec.utils.company_choices import get_company_choices

    with contextlib.suppress(Exception):
        await get_company_choices(use_cache=True)


@router.api_router.get("/as_filed_statement", include_in_schema=False)
async def as_filed_statement(
    symbol: Annotated[str | None, FastAPIQuery(description="Ticker symbol.")] = None,
    statement_type: Annotated[
        str,
        FastAPIQuery(description="balance, income, cash, equity, or comprehensive."),
    ] = "balance",
    calendar_year: Annotated[
        str | None, FastAPIQuery(description="Calendar year of the filing.")
    ] = None,
    calendar_period: Annotated[
        str | None,
        FastAPIQuery(
            description="Calendar quarter (Q1-Q4); empty for the latest filing."
        ),
    ] = None,
    use_cache: Annotated[bool, FastAPIQuery(description="Use the cache.")] = True,
) -> list:
    """As-filed statement pivoted to period-ending columns for a Workspace table."""
    from openbb_sec.utils.as_filed_widget import get_as_filed_widget_rows

    if not symbol:
        return []
    return await get_as_filed_widget_rows(
        symbol.upper(),
        statement_type,
        calendar_year or None,
        calendar_period or None,
        use_cache,
    )


@router.api_router.get("/standardized_statement", include_in_schema=False)
async def standardized_statement(
    symbol: Annotated[str | None, FastAPIQuery(description="Ticker symbol.")] = "AAPL",
    statement_type: Annotated[
        str | None, FastAPIQuery(description="One of: balance, income, cash.")
    ] = "balance",
    period: Annotated[
        str | None, FastAPIQuery(description="One of: FY, Q, TTM.")
    ] = "FY",
    transform: Annotated[
        str | None, FastAPIQuery(description="One of: None, % YoY, % PoP.")
    ] = "None",
    transpose: Annotated[
        bool, FastAPIQuery(description="Pivot line items to rows, periods to columns.")
    ] = True,
    limit: Annotated[
        int, FastAPIQuery(description="Most-recent N periods (0 = all).")
    ] = 10,
) -> list:
    """Standardized SEC financial statement shaped for a Workspace table widget.

    Backs the balance/income/cash widgets with SEC EDGAR companyfacts data,
    standardized via openbb_sec.utils.company_facts.
    """
    from openbb_sec.utils.statement_widget import get_statement_widget_rows

    if not symbol:
        return []
    return await get_statement_widget_rows(
        symbol=symbol.upper(),
        statement_type=statement_type or "",
        period=period or "",
        transform=transform or "",
        transpose=transpose,
        limit=limit,
    )


@router.api_router.get("/widgets.json", include_in_schema=False)
async def get_widgets_json() -> dict:
    """Serve the SEC widgets.json, merged at runtime by the OpenBB API.

    Auto-generates a widget for every currently-registered SEC command, so the
    set adapts when openbb-equity/openbb-etf are absent and their standard models
    register here instead. The curated customizations in assets/widgets.json are
    then overlaid on top.
    """
    import asyncio
    import json
    from pathlib import Path

    task = asyncio.get_running_loop().create_task(_warm_companies())
    _PRIME_TASKS.add(task)
    task.add_done_callback(_PRIME_TASKS.discard)
    ensure_mcp_subprocess()

    curated = json.loads(
        (Path(__file__).parent / "assets" / "widgets.json").read_text(encoding="utf-8")
    )
    mcp_url = _mcp_public_url()
    if "sec_filing_viewer_sec_obb" in curated:
        curated["sec_filing_viewer_sec_obb"]["storage"] = {"mcpUrl": mcp_url}
    try:
        from fastapi import FastAPI
        from openbb_core.app.service.system_service import SystemService
        from openbb_platform_api.utils.widgets import build_json

        # Build the spec from a throwaway app that holds ONLY the SEC router, so
        # widget generation stays isolated to this provider and never imports or
        # builds the whole platform app just to read SEC routes.
        api_prefix = SystemService().system_settings.api_settings.prefix
        sec_prefix = f"{api_prefix}/sec/"
        sec_app = FastAPI()
        sec_app.include_router(router.api_router, prefix=f"{api_prefix}/sec")
        generated = build_json(sec_app.openapi(), [])
        widgets = {
            key: value
            for key, value in generated.items()
            if value.get("endpoint", "").startswith(sec_prefix)
        }
        widgets.update(curated)
        return widgets
    except Exception:  # noqa: BLE001
        return curated


_EQUITY_WIDGET_REMAP = {
    "sec_management_discussion_analysis_sec_obb": (
        "equity_fundamental_management_discussion_analysis_sec_obb"
    ),
    "sec_form_13f_sec_obb": "equity_ownership_form_13f_sec_obb",
}
_ETF_WIDGET_REMAP = {
    "sec_nport_disclosure_sec_obb": "etf_nport_disclosure_sec_obb",
}


def _remap_app_widgets(apps: list, remap: dict) -> list:
    """Rewrite widget ids in tab layouts and groups in place."""
    for app in apps:
        for tab in app.get("tabs", {}).values():
            for widget in tab.get("layout", []):
                widget["i"] = remap.get(widget.get("i"), widget.get("i"))
        for group in app.get("groups", []):
            group["widgetIds"] = [
                remap.get(wid, wid) for wid in group.get("widgetIds", [])
            ]
    return apps


@router.api_router.get("/apps.json", include_in_schema=False)
async def get_apps_json() -> list:
    """Serve the SEC apps.json dashboard template, adapted to the install config."""
    import json
    from pathlib import Path

    path = Path(__file__).parent / "assets" / "apps.json"
    apps = json.loads(path.read_text(encoding="utf-8"))
    remap: dict = {}
    if EQUITY_INSTALLED:
        remap.update(_EQUITY_WIDGET_REMAP)
    if ETF_INSTALLED:
        remap.update(_ETF_WIDGET_REMAP)
    if remap:
        _remap_app_widgets(apps, remap)
    return apps
