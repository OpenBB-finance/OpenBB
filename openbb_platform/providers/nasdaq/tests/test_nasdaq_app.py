"""App tests for Nasdaq provider."""

# flake8: noqa:E501
# pylint: disable=redefined-outer-name, unused-argument, line-too-long

import pytest
from fastapi import FastAPI
from openbb_nasdaq.app import main
from openbb_platform_api.utils.widgets import build_json


@pytest.fixture(scope="module")
def nasdaq_app():
    """Fixture to serve FastAPI app instance."""
    app = main()
    yield app


def test_app_is_fastapi_instance(nasdaq_app):
    """Test that the factory function returns a FastAPI instance."""
    assert isinstance(nasdaq_app, FastAPI)


def test_app_has_routes(nasdaq_app):
    """Test that the app has at least one route."""
    assert len(nasdaq_app.routes) > 0


@pytest.mark.asyncio
async def test_apps_json(nasdaq_app):
    expected = {
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
                    {"i": "nasdaq_company_filings", "x": 0, "y": 12, "w": 40, "h": 30},
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
                                        "leftColIds": ["ipo_date", "symbol", "name"],
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
                    {"i": "nasdaq_economic_calendar", "x": 0, "y": 2, "w": 40, "h": 20}
                ],
            },
        },
        "groups": [],
    }
    route = [d for d in nasdaq_app.routes if d.path == "/apps.json"][0]
    response = await route.endpoint()
    assert isinstance(response, dict)
    assert response == expected


def test_widgets_json(nasdaq_app):
    expected = {
        "nasdaq_company_filings": {
            "name": "SEC Filings",
            "description": "View SEC filings by company.",
            "category": "Open Document",
            "type": "multi_file_viewer",
            "searchCategory": "Open Document",
            "widgetId": "nasdaq_company_filings",
            "params": [
                {
                    "label": "Document URL",
                    "description": "Select the document to open.",
                    "optional": False,
                    "type": "endpoint",
                    "value": None,
                    "show": False,
                    "paramName": "document_url",
                    "optionsEndpoint": "/get_symbol_choices",
                    "optionsParams": {
                        "symbol": "$symbol",
                        "year": "$year",
                        "form_group": "$form_group",
                    },
                    "roles": ["fileSelector"],
                    "multiSelect": True,
                },
                {
                    "paramName": "symbol",
                    "label": "Symbol",
                    "description": "Ticker symbol for the company. Foreign (dual-listed) companies may not be required to file with the SEC.",
                    "type": "endpoint",
                    "value": "AAPL",
                    "optionsEndpoint": "/get_symbol_choices",
                    "style": {"popupWidth": 850},
                },
                {
                    "paramName": "year",
                    "label": "Calendar Year",
                    "description": "Calendar year for the filings.",
                    "value": 2025,
                    "type": "number",
                    "options": [
                        {"label": "2025", "value": 2025},
                        {"label": "2024", "value": 2024},
                        {"label": "2023", "value": 2023},
                        {"label": "2022", "value": 2022},
                        {"label": "2021", "value": 2021},
                        {"label": "2020", "value": 2020},
                        {"label": "2019", "value": 2019},
                        {"label": "2018", "value": 2018},
                        {"label": "2017", "value": 2017},
                        {"label": "2016", "value": 2016},
                        {"label": "2015", "value": 2015},
                        {"label": "2014", "value": 2014},
                        {"label": "2013", "value": 2013},
                        {"label": "2012", "value": 2012},
                        {"label": "2011", "value": 2011},
                        {"label": "2010", "value": 2010},
                        {"label": "2009", "value": 2009},
                        {"label": "2008", "value": 2008},
                        {"label": "2007", "value": 2007},
                        {"label": "2006", "value": 2006},
                        {"label": "2005", "value": 2005},
                        {"label": "2004", "value": 2004},
                        {"label": "2003", "value": 2003},
                        {"label": "2002", "value": 2002},
                        {"label": "2001", "value": 2001},
                        {"label": "2000", "value": 2000},
                        {"label": "1999", "value": 1999},
                        {"label": "1998", "value": 1998},
                        {"label": "1997", "value": 1997},
                        {"label": "1996", "value": 1996},
                        {"label": "1995", "value": 1995},
                        {"label": "1994", "value": 1994},
                    ],
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
            "endpoint": "open_document",
            "runButton": False,
            "gridData": {"w": 40, "h": 30},
            "data": {"dataKey": "", "table": {"showAll": True}},
            "source": ["Custom"],
            "refetchInterval": False,
        },
        "nasdaq_earnings_calendar": {
            "name": "Earnings Calendar",
            "description": "Upcoming, and historical, company earnings releases (US Markets).",
            "category": "Equity",
            "type": "table",
            "searchCategory": "Equity",
            "widgetId": "nasdaq_earnings_calendar",
            "params": [
                {
                    "label": "Start Date",
                    "description": "Start date of the data.",
                    "optional": True,
                    "type": "date",
                    "value": None,
                    "show": True,
                    "paramName": "start_date",
                },
                {
                    "label": "End Date",
                    "description": "End date of the data.",
                    "optional": True,
                    "type": "date",
                    "value": None,
                    "show": True,
                    "paramName": "end_date",
                },
            ],
            "endpoint": "earnings_calendar",
            "runButton": False,
            "gridData": {"w": 40, "h": 20},
            "data": {
                "dataKey": "",
                "table": {
                    "showAll": True,
                    "columnsDefs": [
                        {
                            "field": "report_date",
                            "formatterFn": None,
                            "headerName": "Report Date",
                            "headerTooltip": "The date of the earnings report.",
                            "cellDataType": "date",
                        },
                        {
                            "field": "symbol",
                            "pinned": "left",
                            "formatterFn": None,
                            "headerName": "Symbol",
                            "headerTooltip": "Symbol representing the entity requested in the data.",
                            "cellDataType": "text",
                        },
                        {
                            "field": "name",
                            "pinned": "left",
                            "formatterFn": None,
                            "headerName": "Name",
                            "headerTooltip": "Name of the entity.",
                            "cellDataType": "text",
                        },
                        {
                            "field": "eps_previous",
                            "formatterFn": None,
                            "headerName": "EPS Previous",
                            "headerTooltip": "The earnings-per-share from the same previously reported period.",
                            "cellDataType": "number",
                        },
                        {
                            "field": "eps_consensus",
                            "formatterFn": None,
                            "headerName": "EPS Consensus",
                            "headerTooltip": "The analyst conesus earnings-per-share estimate.",
                            "cellDataType": "number",
                        },
                        {
                            "field": "eps_actual",
                            "formatterFn": None,
                            "headerName": "EPS Actual",
                            "headerTooltip": "The actual earnings per share (USD) announced.",
                            "cellDataType": "number",
                        },
                        {
                            "field": "surprise_percent",
                            "formatterFn": "normalizedPercent",
                            "headerName": "Surprise Percent",
                            "headerTooltip": "The earnings surprise as normalized percentage points.",
                            "cellDataType": "number",
                            "renderFn": "greenRed",
                        },
                        {
                            "field": "num_estimates",
                            "formatterFn": None,
                            "headerName": "Num Estimates",
                            "headerTooltip": "The number of analysts providing estimates for the consensus.",
                            "cellDataType": "number",
                        },
                        {
                            "field": "period_ending",
                            "pinned": "left",
                            "formatterFn": None,
                            "headerName": "Period Ending",
                            "headerTooltip": "The fiscal period end date.",
                            "cellDataType": "text",
                        },
                        {
                            "field": "previous_report_date",
                            "formatterFn": None,
                            "headerName": "Previous Report Date",
                            "headerTooltip": "The previous report date for the same period last year.",
                            "cellDataType": "date",
                        },
                        {
                            "field": "reporting_time",
                            "formatterFn": None,
                            "headerName": "Reporting Time",
                            "headerTooltip": "The reporting time - e.g. after market close.",
                            "cellDataType": "text",
                        },
                        {
                            "field": "market_cap",
                            "formatterFn": None,
                            "headerName": "Market Cap",
                            "headerTooltip": "The market cap (USD) of the reporting entity.",
                            "cellDataType": "number",
                        },
                    ],
                },
            },
            "source": ["Custom"],
            "subCategory": "Calendar",
            "refetchInterval": False,
        },
        "nasdaq_dividends_calendar": {
            "name": "Dividend Calendar",
            "description": "Upcoming, and historical, dividend payments (US Markets).",
            "category": "Equity",
            "type": "table",
            "searchCategory": "Equity",
            "widgetId": "nasdaq_dividends_calendar",
            "params": [
                {
                    "label": "Start Date",
                    "description": "Start date of the data.",
                    "optional": True,
                    "type": "date",
                    "value": None,
                    "show": True,
                    "paramName": "start_date",
                },
                {
                    "label": "End Date",
                    "description": "End date of the data.",
                    "optional": True,
                    "type": "date",
                    "value": None,
                    "show": True,
                    "paramName": "end_date",
                },
            ],
            "endpoint": "dividend_calendar",
            "runButton": False,
            "gridData": {"w": 40, "h": 20},
            "data": {
                "dataKey": "",
                "table": {
                    "showAll": True,
                    "columnsDefs": [
                        {
                            "field": "ex_dividend_date",
                            "formatterFn": None,
                            "headerName": "Ex Dividend Date",
                            "headerTooltip": "The ex-dividend date - the date on which the stock begins trading without rights to the dividend.",
                            "cellDataType": "date",
                        },
                        {
                            "field": "symbol",
                            "pinned": "left",
                            "formatterFn": None,
                            "headerName": "Symbol",
                            "headerTooltip": "Symbol representing the entity requested in the data.",
                            "cellDataType": "text",
                        },
                        {
                            "field": "amount",
                            "formatterFn": None,
                            "headerName": "Amount",
                            "headerTooltip": "The dividend amount per share.",
                            "cellDataType": "number",
                        },
                        {
                            "field": "name",
                            "pinned": "left",
                            "formatterFn": None,
                            "headerName": "Name",
                            "headerTooltip": "Name of the entity.",
                            "cellDataType": "text",
                        },
                        {
                            "field": "record_date",
                            "formatterFn": None,
                            "headerName": "Record Date",
                            "headerTooltip": "The record date of ownership for eligibility.",
                            "cellDataType": "date",
                        },
                        {
                            "field": "payment_date",
                            "formatterFn": None,
                            "headerName": "Payment Date",
                            "headerTooltip": "The payment date of the dividend.",
                            "cellDataType": "date",
                        },
                        {
                            "field": "declaration_date",
                            "formatterFn": None,
                            "headerName": "Declaration Date",
                            "headerTooltip": "Declaration date of the dividend.",
                            "cellDataType": "date",
                        },
                        {
                            "field": "annualized_amount",
                            "formatterFn": None,
                            "headerName": "Annualized Amount",
                            "headerTooltip": "The indicated annualized dividend amount.",
                            "cellDataType": "number",
                        },
                    ],
                },
            },
            "source": ["Custom"],
            "subCategory": "Calendar",
            "refetchInterval": False,
        },
        "nasdaq_ipo_calendar": {
            "name": "IPO Calendar",
            "description": "IPO announcements and calendar.",
            "category": "Equity",
            "type": "table",
            "searchCategory": "Equity",
            "widgetId": "nasdaq_ipo_calendar",
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
            "endpoint": "ipo_calendar",
            "runButton": False,
            "gridData": {"w": 40, "h": 20},
            "data": {
                "dataKey": "",
                "table": {
                    "showAll": True,
                    "columnsDefs": [
                        {
                            "field": "symbol",
                            "pinned": "left",
                            "formatterFn": None,
                            "headerName": "Symbol",
                            "headerTooltip": "Symbol representing the entity requested in the data.",
                            "cellDataType": "text",
                        },
                        {
                            "field": "ipo_date",
                            "formatterFn": None,
                            "headerName": "IPO Date",
                            "headerTooltip": "The date of the IPO, when the stock first trades on a major exchange.",
                            "cellDataType": "date",
                        },
                        {
                            "field": "name",
                            "pinned": "left",
                            "formatterFn": None,
                            "headerName": "Name",
                            "headerTooltip": "The name of the company.",
                            "cellDataType": "text",
                        },
                        {
                            "field": "offer_amount",
                            "formatterFn": None,
                            "headerName": "Offer Amount",
                            "headerTooltip": "The dollar value of the shares offered.",
                            "cellDataType": "number",
                        },
                        {
                            "field": "share_count",
                            "formatterFn": None,
                            "headerName": "Share Count",
                            "headerTooltip": "The number of shares offered.",
                            "cellDataType": "number",
                        },
                        {
                            "field": "expected_price_date",
                            "formatterFn": None,
                            "headerName": "Expected Price Date",
                            "headerTooltip": "The date the pricing is expected.",
                            "cellDataType": "date",
                        },
                        {
                            "field": "filed_date",
                            "formatterFn": None,
                            "headerName": "Filed Date",
                            "headerTooltip": "The date the IPO was filed.",
                            "cellDataType": "date",
                        },
                        {
                            "field": "withdraw_date",
                            "formatterFn": None,
                            "headerName": "Withdraw Date",
                            "headerTooltip": "The date the IPO was withdrawn.",
                            "cellDataType": "date",
                        },
                        {
                            "field": "deal_status",
                            "formatterFn": None,
                            "headerName": "Deal Status",
                            "headerTooltip": "The status of the deal.",
                            "cellDataType": "text",
                        },
                    ],
                },
            },
            "source": ["Custom"],
            "subCategory": "Calendar",
            "refetchInterval": False,
        },
        "nasdaq_economic_calendar": {
            "name": "Economic Calendar",
            "description": "Upcoming, and historical, macroeconomic events.",
            "category": "Economy",
            "type": "table",
            "searchCategory": "Equity",
            "widgetId": "nasdaq_economic_calendar",
            "params": [
                {
                    "label": "Start Date",
                    "description": "Start Date",
                    "optional": True,
                    "type": "date",
                    "value": None,
                    "show": True,
                    "paramName": "start_date",
                },
                {
                    "label": "End Date",
                    "description": "End Date",
                    "optional": True,
                    "type": "date",
                    "value": None,
                    "show": True,
                    "paramName": "end_date",
                },
                {
                    "label": "Country",
                    "description": "Country",
                    "optional": True,
                    "type": "text",
                    "value": None,
                    "show": True,
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
            "endpoint": "economic_calendar",
            "runButton": False,
            "gridData": {"w": 40, "h": 20},
            "data": {
                "dataKey": "",
                "table": {
                    "showAll": False,
                    "columnsDefs": [
                        {
                            "field": "date",
                            "pinned": "left",
                            "headerName": "Date",
                            "headerTooltip": "The date of the data.",
                            "cellDataType": "date",
                        },
                        {
                            "field": "country",
                            "headerName": "Country",
                            "headerTooltip": "Country of event.",
                            "cellDataType": "text",
                        },
                        {
                            "field": "event",
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
                            "headerName": "Consensus",
                            "headerTooltip": "Average forecast among a representative group of economists.",
                            "cellDataType": "number",
                        },
                        {
                            "field": "actual",
                            "headerName": "Actual",
                            "headerTooltip": "Latest released value.",
                            "cellDataType": "number",
                        },
                        {
                            "field": "previous",
                            "headerName": "Previous",
                            "headerTooltip": "Value for the previous period after the revision (if revision is applicable).",
                            "cellDataType": "number",
                        },
                        {
                            "field": "revised",
                            "headerName": "Revised",
                            "headerTooltip": "Revised previous value, if applicable.",
                            "cellDataType": "number",
                        },
                    ],
                },
            },
            "source": ["Custom"],
            "subCategory": "Calendar",
            "refetchInterval": False,
        },
    }

    openapi_json: dict = nasdaq_app.openapi()
    assert isinstance(openapi_json, dict)
    response = build_json(openapi_json, [])
    assert isinstance(response, dict)
    assert response == expected
