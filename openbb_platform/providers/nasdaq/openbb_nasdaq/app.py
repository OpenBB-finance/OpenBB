"""OpenBB Workspace Application.

This includes widgets and endpoints for fetching and displaying
SEC filings, as well as calendars for earnings, dividends, ipos,
and global economic events from the public Nasdaq website.

To use this app, launch it with:

```bash
openbb-api --app openbb_nasdaq.app:main --factory
```

Then navigate to the OpenBB Workspace and add the server as a backend data source.

Open the server's URL in your browser for more information on connecting to the OpenBB Workspace.
"""

# pylint: disable=too-many-statements, too-many-locals, line-too-long


def main():
    """Return a FastAPI app instance."""
    # pylint: disable=import-outside-toplevel
    from datetime import datetime
    from typing import Annotated, Any, Literal, Optional

    from async_lru import alru_cache
    from fastapi import Depends, FastAPI
    from openbb_nasdaq.models.calendar_dividend import NasdaqCalendarDividendFetcher
    from openbb_nasdaq.models.calendar_earnings import NasdaqCalendarEarningsFetcher
    from openbb_nasdaq.models.calendar_ipo import NasdaqCalendarIpoFetcher
    from openbb_nasdaq.models.company_filings import NasdaqCompanyFilingsFetcher
    from openbb_nasdaq.models.economic_calendar import NasdaqEconomicCalendarFetcher
    from openbb_nasdaq.models.equity_search import NasdaqEquitySearchFetcher
    from pandas import DataFrame

    listings = DataFrame()

    current_year = int(datetime.now().year)
    years = sorted(
        [{"label": str(i), "value": i} for i in range(1994, current_year + 1)],
        key=lambda x: x["value"],  # type: ignore
        reverse=True,
    )

    app = FastAPI()

    async def get_listings() -> DataFrame:
        """Get the Nasdaq listings."""
        return listings

    Nasdaqlistings = Annotated[
        DataFrame,
        Depends(get_listings),
    ]

    async def startup_event():
        """Startup event for the FastAPI app."""
        nonlocal listings
        fetcher = NasdaqEquitySearchFetcher()

        directory = await fetcher.fetch_data({}, {})

        listings = DataFrame([d.model_dump() for d in directory]).query(  # type: ignore
            "test_issue == 'N' and etf == 'N'"
            " and not name.str.contains('%')"
            " and not name.str.contains('Unit')"
            " and not name.str.contains('Rights')"
            " and not name.str.contains('Warrant')"
            " and not name.str.contains('Preferred')"
        )

    app.add_event_handler("startup", startup_event)

    @app.get("/get_symbol_choices", include_in_schema=False)
    async def get_symbol_choices(
        directory: Nasdaqlistings,  # type: ignore
        symbol: Optional[str] = None,
        year: Optional[int] = None,
        form_group: Optional[str] = None,
    ) -> list:
        """Get symbol choices for the Nasdaq listings."""

        if symbol and year and form_group:
            return await get_document_choices(symbol, year, form_group)

        items = directory.set_index("symbol")["name"].to_dict()

        return [
            {"value": k, "label": k, "extraInfo": {"description": v}}
            for k, v in items.items()
        ]

    @alru_cache
    async def get_document_choices(
        symbol: Optional[str] = None,
        year: Optional[int] = None,
        form_group: Literal[
            "annual",
            "quarterly",
            "proxy",
            "insider",
            "8k",
            "registration",
            "comment",
        ] = "8k",
    ) -> list:
        """Get document choices for the given symbol."""
        fetcher = NasdaqCompanyFilingsFetcher()

        params = {
            "symbol": symbol,
            "year": year,
            "form_group": form_group,
        }

        items = await fetcher.fetch_data(params, {})
        docs: list = []

        for item in items:
            form = item.model_dump()  # type: ignore
            title = f"{form.get('filing_date', '')} - {'8-K' if form_group == '8k' else form_group.title()}"
            url = form.get("pdf_url")

            if not url:
                continue
            docs.append({"label": title, "value": url})

        return docs

    @alru_cache(maxsize=128)
    async def download_pdf_file(document_url: str):
        """Download a PDF file from the given URL."""
        # pylint: disable=import-outside-toplevel
        import base64  # noqa
        from openbb_core.provider.utils.helpers import make_request

        response = make_request(document_url)
        response.raise_for_status()
        encoded_content = base64.b64encode(response.content).decode("utf-8")

        return encoded_content

    @app.get(
        "/open_document",
        openapi_extra={
            "widget_config": {
                "type": "multi_file_viewer",
                "name": "SEC Filings",
                "description": "View SEC filings by company.",
                "refetchInterval": False,
                "widgetId": "nasdaq_company_filings",
                "params": [
                    {
                        "paramName": "document_url",
                        "label": "Document URL",
                        "description": "Select the document to open.",
                        "type": "endpoint",
                        "optionsEndpoint": "/get_symbol_choices",
                        "optionsParams": {
                            "symbol": "$symbol",
                            "year": "$year",
                            "form_group": "$form_group",
                        },
                        "show": False,
                        "roles": ["fileSelector"],
                        "multiSelect": True,
                    },
                    {
                        "paramName": "symbol",
                        "label": "Symbol",
                        "description": (
                            "Ticker symbol for the company."
                            " Foreign (dual-listed) companies may not be required to file with the SEC."
                        ),
                        "type": "endpoint",
                        "value": "AAPL",
                        "optionsEndpoint": "/get_symbol_choices",
                        "style": {"popupWidth": 850},
                    },
                    {
                        "paramName": "year",
                        "label": "Calendar Year",
                        "description": "Calendar year for the filings.",
                        "value": years[0]["value"],
                        "type": "number",
                        "options": years,
                    },
                    {
                        "paramName": "form_group",
                        "label": "Form Group",
                        "description": "Form group for the filings.",
                        "value": "8k",
                        "type": "text",
                        "options": [
                            {"label": "Annual", "value": "annual"},
                            {"label": "Quarterly", "value": "quarterly"},
                            {"label": "Proxy", "value": "proxy"},
                            {"label": "Insider", "value": "insider"},
                            {"label": "8-K", "value": "8k"},
                            {"label": "Registration", "value": "registration"},
                            {"label": "Comment", "value": "comment"},
                        ],
                    },
                ],
                "gridData": {"w": 40, "h": 30},
            }
        },
    )
    async def open_document(
        document_url: str,
    ) -> dict[str, Any]:
        """Open the selected PDF filing document."""
        encoded_content: str = ""
        error_message: str = ""

        try:
            if document_url and document_url.startswith("http"):
                encoded_content = await download_pdf_file(document_url)

        except Exception as e:  # pylint: disable=broad-except
            error_message = f"Error fetching document: {e.args[0]}"

        symbol = document_url.split("&symbol=", maxsplit=1)[1].split("&", maxsplit=1)[0]
        form_type = (
            document_url.split("&formType=", maxsplit=1)[1]
            .split("&", maxsplit=1)[0]
            .replace("-", "")
        )
        date_str = document_url.split("&dateFiled=", maxsplit=1)[1][:10].replace(
            "-", ""
        )
        filename = f"{symbol}-{date_str}-{form_type}.pdf"
        content: dict[str, Any] = {}
        if error_message != "":
            content = {
                "error_type": "download_error",
                "content": error_message,
            }
        else:
            content = {
                "content": encoded_content,
                "data_format": {
                    "data_type": "pdf",
                    "filename": filename,
                },
            }

        return content

    @app.post(
        "/open_document",
        include_in_schema=False,
    )
    async def post_open_document(
        params: dict,
    ) -> list:
        """POST request to open the selected PDF filing document(s)."""
        urls = params.get("document_url", [])
        documents: list = []
        if urls:
            for document_url in urls:
                if document_url.startswith("http"):
                    document = await open_document(document_url)
                    if document:
                        documents.append(document)

        return documents

    @app.get(
        "/earnings_calendar",
        openapi_extra={
            "widget_config": {
                "name": "Earnings Calendar",
                "description": "Upcoming, and historical, company earnings releases (US Markets).",
                "category": "Equity",
                "subCategory": "Calendar",
                "type": "table",
                "searchCategory": "Equity",
                "widgetId": "nasdaq_earnings_calendar",
                "refetchInterval": False,
                "params": [
                    {
                        "label": "Start Date",
                        "description": "Start date of the data.",
                        "type": "date",
                        "value": None,
                        "paramName": "start_date",
                    },
                    {
                        "label": "End Date",
                        "description": "End date of the data.",
                        "type": "date",
                        "value": None,
                        "paramName": "end_date",
                    },
                ],
                "gridData": {"w": 40, "h": 20},
                "data": {
                    "table": {
                        "columnsDefs": [
                            {
                                "field": "surprise_percent",
                                "formatterFn": "normalizedPercent",
                                "cellDataType": "number",
                                "renderFn": "greenRed",
                            },
                        ]
                    }
                },
            },
        },
    )
    async def earnings_calendar(
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> list[NasdaqCalendarEarningsFetcher.data_type]:
        """Get the earnings calendar."""
        fetcher = NasdaqCalendarEarningsFetcher()

        params = {
            "start_date": start_date,
            "end_date": end_date,
        }

        return await fetcher.fetch_data(params, {})  # type: ignore

    @app.get(
        "/dividend_calendar",
        openapi_extra={
            "widget_config": {
                "name": "Dividend Calendar",
                "description": "Upcoming, and historical, dividend payments (US Markets).",
                "category": "Equity",
                "subCategory": "Calendar",
                "type": "table",
                "searchCategory": "Equity",
                "widgetId": "nasdaq_dividends_calendar",
                "refetchInterval": False,
                "params": [
                    {
                        "label": "Start Date",
                        "description": "Start date of the data.",
                        "type": "date",
                        "value": None,
                        "paramName": "start_date",
                    },
                    {
                        "label": "End Date",
                        "description": "End date of the data.",
                        "type": "date",
                        "value": None,
                        "paramName": "end_date",
                    },
                ],
                "gridData": {"w": 40, "h": 20},
            }
        },
    )
    async def dividend_calendar(
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> list[NasdaqCalendarDividendFetcher.data_type]:
        """Get the dividend calendar."""
        fetcher = NasdaqCalendarDividendFetcher()

        params = {
            "start_date": start_date,
            "end_date": end_date,
        }

        return await fetcher.fetch_data(params, {})  # type: ignore

    @app.get(
        "/ipo_calendar",
        openapi_extra={
            "widget_config": {
                "name": "IPO Calendar",
                "description": "IPO announcements and calendar.",
                "category": "Equity",
                "subCategory": "Calendar",
                "type": "table",
                "searchCategory": "Equity",
                "widgetId": "nasdaq_ipo_calendar",
                "refetchInterval": False,
                "params": [
                    {
                        "label": "Start Date",
                        "description": "Start date of the data, in YYYY-MM-DD format.",
                        "optional": True,
                        "type": "date",
                        "value": None,
                        "show": True,
                        "paramName": "start_date",
                    },
                    {
                        "label": "End Date",
                        "description": "End date of the data, in YYYY-MM-DD format.",
                        "optional": True,
                        "type": "date",
                        "value": None,
                        "show": True,
                        "paramName": "end_date",
                    },
                    {
                        "label": "Status",
                        "description": "Status of the IPO. [upcoming, priced, or withdrawn]",
                        "optional": True,
                        "type": "text",
                        "value": None,
                        "show": True,
                        "options": [
                            {"label": "upcoming", "value": "upcoming"},
                            {"label": "priced", "value": "priced"},
                            {"label": "filed", "value": "filed"},
                            {"label": "withdrawn", "value": "withdrawn"},
                        ],
                        "paramName": "status",
                    },
                    {
                        "label": "Is SPO",
                        "description": "If True, returns data for secondary public offerings (SPOs).",
                        "optional": True,
                        "type": "boolean",
                        "value": False,
                        "show": True,
                        "paramName": "is_spo",
                    },
                ],
                "gridData": {"w": 40, "h": 20},
            }
        },
    )
    async def ipo_calendar(
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> list[NasdaqCalendarIpoFetcher.data_type]:
        """Get the IPO calendar."""
        fetcher = NasdaqCalendarIpoFetcher()

        params = {
            "start_date": start_date,
            "end_date": end_date,
        }

        return await fetcher.fetch_data(params, {})  # type: ignore

    @app.get(
        "/economic_calendar",
        openapi_extra={
            "widget_config": {
                "name": "Economic Calendar",
                "description": "Upcoming, and historical, macroeconomic events.",
                "category": "Economy",
                "subCategory": "Calendar",
                "type": "table",
                "searchCategory": "Equity",
                "widgetId": "nasdaq_economic_calendar",
                "refetchInterval": False,
                "params": [
                    {
                        "paramName": "country",
                        "options": [
                            {"label": "United States", "value": "united_states"},
                            {"label": "China", "value": "china"},
                            {"label": "Hong Kong", "value": "hong_kong"},
                            {"label": "Japan", "value": "japan"},
                            {"label": "Singapore", "value": "signapore"},
                            {"label": "South Korea", "value": "south_korea"},
                            {"label": "India", "value": "india"},
                            {"label": "Russia", "value": "russia"},
                            {"label": "Euro Zone", "value": "euro_zone"},
                            {"label": "Germany", "value": "germany"},
                            {"label": "United Kingdom", "value": "united_kingdom"},
                            {"label": "France", "value": "france"},
                            {"label": "Spain", "value": "spain"},
                            {"label": "Italy", "value": "italy"},
                            {"label": "Switzerland", "value": "switzerland"},
                            {"label": "Canada", "value": "canada"},
                            {"label": "Australia", "value": "australia"},
                            {"label": "New Zealand", "value": "new_zealand"},
                            {"label": "South Africa", "value": "south_africa"},
                            {"label": "Brazil", "value": "brazil"},
                        ],
                    },
                ],
                "gridData": {"w": 40, "h": 20},
                "data": {
                    "table": {
                        "showAll": False,
                        "columnsDefs": [
                            {
                                "field": "date",
                                "pinned": "left",
                                "formatterFn": None,
                                "headerName": "Date",
                                "headerTooltip": "The date of the data.",
                                "cellDataType": "date",
                            },
                            {
                                "field": "country",
                                "formatterFn": None,
                                "headerName": "Country",
                                "headerTooltip": "Country of event.",
                                "cellDataType": "text",
                            },
                            {
                                "field": "event",
                                "formatterFn": None,
                                "renderFn": "hoverCard",
                                "renderFnParams": {
                                    "hoverCard": {
                                        "cellField": "value",
                                        "markdown": "{description}",
                                    }
                                },
                                "headerName": "Event",
                                "headerTooltip": "Event name.",
                                "cellDataType": "text",
                            },
                            {
                                "field": "consensus",
                                "formatterFn": None,
                                "headerName": "Consensus",
                                "headerTooltip": "Average forecast among a representative group of economists.",
                                "cellDataType": "number",
                            },
                            {
                                "field": "actual",
                                "formatterFn": None,
                                "headerName": "Actual",
                                "headerTooltip": "Latest released value.",
                                "cellDataType": "number",
                            },
                            {
                                "field": "previous",
                                "formatterFn": None,
                                "headerName": "Previous",
                                "headerTooltip": (
                                    "Value for the previous period after"
                                    + " the revision (if revision is applicable)."
                                ),
                                "cellDataType": "number",
                            },
                            {
                                "field": "revised",
                                "formatterFn": None,
                                "headerName": "Revised",
                                "headerTooltip": "Revised previous value, if applicable.",
                                "cellDataType": "number",
                            },
                        ],
                    }
                },
            }
        },
    )
    async def economic_calendar(
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        country: Optional[str] = None,
    ):
        """Get the dividend calendar."""
        fetcher = NasdaqEconomicCalendarFetcher()

        params = {
            "start_date": start_date,
            "end_date": end_date,
        }
        if country:
            params["country"] = country

        data: list[NasdaqEconomicCalendarFetcher.data_type] = await fetcher.fetch_data(params, {})  # type: ignore
        output: list = []

        for row in data:
            markdown = (
                f"### **{row.event}**\n\n{row.description}"
                if row.description
                else row.event
            )
            output.append(
                {
                    "date": row.date.strftime("%Y-%m-%d"),
                    "country": row.country,
                    "event": {
                        "value": row.event,
                        "description": markdown,
                    },
                    "consensus": row.consensus,
                    "actual": row.actual,
                    "previous": row.previous,
                    "revised": row.revised,
                }
            )

        return output

    @app.get(
        "/apps.json",
        include_in_schema=False,
    )
    async def get_apps() -> dict:
        return {
            "name": "Company Filings & Market Calendars",
            "img": "https://logosandtypes.com/wp-content/uploads/2020/07/nasdaq.svg",
            "img_dark": "",
            "img_light": "",
            "description": (
                "View company filings and market calendars, downloaded from the public Nasdaq website."
                " This app is not affiliated with, or authoriazed by, Nasdaq."
            ),
            "allowCustomization": True,
            "tabs": {
                "earnings": {
                    "id": "earnings",
                    "name": "Earnings Calendar & Filings",
                    "layout": [
                        {
                            "i": "nasdaq_earnings_calendar",
                            "x": 0,
                            "y": 2,
                            "w": 40,
                            "h": 10,
                            "state": {
                                "chartView": {"enabled": False, "chartType": "line"},
                                "columnState": {
                                    "default": {
                                        "sort": {
                                            "sortModel": [
                                                {"colId": "market_cap", "sort": "desc"}
                                            ]
                                        },
                                        "columnPinning": {
                                            "leftColIds": [
                                                "symbol",
                                                "name",
                                                "period_ending",
                                            ],
                                            "rightColIds": [],
                                        },
                                        "columnOrder": {
                                            "orderedColIds": [
                                                "report_date",
                                                "reporting_time",
                                                "symbol",
                                                "name",
                                                "market_cap",
                                                "eps_previous",
                                                "eps_consensus",
                                                "num_estimates",
                                                "eps_actual",
                                                "surprise_percent",
                                                "period_ending",
                                                "previous_report_date",
                                            ]
                                        },
                                    }
                                },
                            },
                        },
                        {
                            "i": "nasdaq_company_filings",
                            "x": 0,
                            "y": 12,
                            "w": 40,
                            "h": 30,
                        },
                    ],
                },
                "dividend-calendar": {
                    "id": "dividend-calendar",
                    "name": "Dividend Calendar",
                    "layout": [
                        {
                            "i": "nasdaq_dividends_calendar",
                            "x": 0,
                            "y": 2,
                            "w": 40,
                            "h": 20,
                            "state": {
                                "chartView": {"enabled": False, "chartType": "line"},
                                "columnState": {
                                    "default": {
                                        "sort": {
                                            "sortModel": [
                                                {
                                                    "colId": "ex_dividend_date",
                                                    "sort": "asc",
                                                },
                                                {"colId": "amount", "sort": "desc"},
                                                {
                                                    "colId": "annualized_amount",
                                                    "sort": "desc",
                                                },
                                            ]
                                        },
                                        "columnPinning": {
                                            "leftColIds": ["symbol", "name"],
                                            "rightColIds": [],
                                        },
                                        "columnOrder": {
                                            "orderedColIds": [
                                                "ex_dividend_date",
                                                "symbol",
                                                "amount",
                                                "name",
                                                "record_date",
                                                "payment_date",
                                                "declaration_date",
                                                "annualized_amount",
                                            ]
                                        },
                                    }
                                },
                            },
                        }
                    ],
                },
                "ipo-calendar": {
                    "id": "ipo-calendar",
                    "name": "IPO Calendar",
                    "layout": [
                        {
                            "i": "nasdaq_ipo_calendar",
                            "x": 0,
                            "y": 2,
                            "w": 40,
                            "h": 21,
                            "state": {
                                "chartView": {"enabled": False, "chartType": "line"},
                                "columnState": {
                                    "default": {
                                        "columnPinning": {
                                            "leftColIds": [
                                                "ipo_date",
                                                "symbol",
                                                "name",
                                            ],
                                            "rightColIds": [],
                                        },
                                        "columnOrder": {
                                            "orderedColIds": [
                                                "ipo_date",
                                                "symbol",
                                                "name",
                                                "offer_amount",
                                                "share_count",
                                                "share_price",
                                                "deal_status",
                                                "exchange",
                                                "id",
                                            ]
                                        },
                                    }
                                },
                            },
                        }
                    ],
                },
                "economic-calendar": {
                    "id": "economic-calendar",
                    "name": "Economic Calendar",
                    "layout": [
                        {
                            "i": "nasdaq_economic_calendar",
                            "x": 0,
                            "y": 2,
                            "w": 40,
                            "h": 20,
                        }
                    ],
                },
            },
            "groups": [],
        }

    return app
